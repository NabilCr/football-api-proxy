from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import httpx

from cache import cache
from config import (
    RAPIDAPI_BASE_URL,
    RAPIDAPI_HEADERS,
    POSTS_BASE_URL,
    TTL_LIVE,
    TTL_SHORT,
    TTL_MEDIUM,
    TTL_LONG,
    TTL_DAY,
)

app = FastAPI(title="Football API Proxy", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ─── Helper ───────────────────────────────────────────────────────────────────

async def proxy(path: str, params: dict, ttl: int, base_url: str = RAPIDAPI_BASE_URL, headers: dict = RAPIDAPI_HEADERS):
    """Fetch from upstream with caching. Returns parsed JSON."""
    # Remove None values so they don't appear in the URL
    clean_params = {k: v for k, v in params.items() if v is not None}
    cache_key = path + str(sorted(clean_params.items()))

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    url = f"{base_url}{path}"
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(url, params=clean_params, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    data = response.json()
    cache.set(cache_key, data, ttl)
    return data


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/matches")
async def matches(
    date: Optional[str] = None,
    lang: Optional[str] = None,
    theme: Optional[str] = None,
    time: Optional[str] = None,
):
    """Live & upcoming matches. Cached 60 seconds."""
    return await proxy("/v3/matches", {"date": date, "lang": lang, "theme": theme, "time": time}, TTL_LIVE)


@app.get("/match/details")
async def match_details(
    id: str = Query(...),
    lang: Optional[str] = None,
    time: Optional[str] = None,
    theme: Optional[str] = None,
):
    """Match details & events. Cached 60 seconds (live updates)."""
    return await proxy("/v3/match/details", {"id": id, "lang": lang, "time": time, "theme": theme}, TTL_LIVE)


@app.get("/standings/league")
async def league_standing(
    id: str = Query(...),
    lang: Optional[str] = None,
    theme: Optional[str] = None,
    time: Optional[str] = None,
    seasonNum: Optional[str] = None,
):
    """League standings table. Cached 1 hour."""
    return await proxy(
        "/v2/league/standing",
        {"id": id, "lang": lang, "theme": theme, "time": time, "seasonNum": seasonNum},
        TTL_LONG,
    )


@app.get("/standings/team")
async def team_standing(
    id: str = Query(...),
    league: Optional[str] = None,
    lang: Optional[str] = None,
    theme: Optional[str] = None,
    time: Optional[str] = None,
):
    """Team standing in a league. Cached 1 hour."""
    return await proxy(
        "/v2/team/standing",
        {"id": id, "league": league, "lang": lang, "theme": theme, "time": time},
        TTL_LONG,
    )


@app.get("/player")
async def player(
    id: str = Query(...),
    lang: Optional[str] = None,
    theme: Optional[str] = None,
    time: Optional[str] = None,
):
    """Player profile & stats. Cached 24 hours."""
    return await proxy("/v2/player", {"id": id, "lang": lang, "theme": theme, "time": time}, TTL_DAY)


@app.get("/statistics")
async def statistics(
    id: str = Query(...),
    lang: Optional[str] = None,
):
    """Match/competition statistics. Cached 30 minutes."""
    return await proxy("/v2/stats", {"id": id, "lang": lang}, TTL_MEDIUM)


@app.get("/countries")
async def countries(lang: Optional[str] = None):
    """Countries & competitions list. Cached 24 hours."""
    return await proxy("/v2/competitions/countries", {"lang": lang}, TTL_DAY)


@app.get("/h2h")
async def h2h(
    id: str = Query(...),
    lang: Optional[str] = None,
    theme: Optional[str] = None,
    time: Optional[str] = None,
):
    """Head-to-head data. Cached 1 hour."""
    return await proxy("/v2/h2h", {"id": id, "lang": lang, "theme": theme, "time": time}, TTL_LONG)


@app.get("/highlights")
async def highlights(
    id: Optional[str] = "167,7,11",
    lang: Optional[str] = None,
    competitors: Optional[str] = None,
):
    """Match highlights. Cached 30 minutes."""
    return await proxy(
        "/v3/highlights",
        {"id": id, "lang": lang, "competitors": competitors},
        TTL_MEDIUM,
    )


@app.get("/posts")
async def posts(
    lang: Optional[str] = None,
    page: Optional[int] = None,
):
    """Football news/posts. Cached 30 minutes."""
    return await proxy("/news", {"lang": lang, "page": page}, TTL_MEDIUM, base_url=POSTS_BASE_URL, headers={})


@app.get("/matches/league")
async def matches_league(
    id: str = Query(...),
    page: Optional[str] = None,
    type: Optional[str] = None,
    lang: Optional[str] = None,
    time: Optional[str] = None,
):
    """Matches by league. Cached 5 minutes."""
    return await proxy(
        "/v3/matches/league",
        {"id": id, "page": page, "type": type, "lang": lang, "time": time},
        TTL_SHORT,
    )


@app.get("/matches/team")
async def matches_team(
    id: str = Query(...),
    page: Optional[str] = None,
    type: Optional[str] = None,
    lang: Optional[str] = None,
    theme: Optional[str] = None,
    time: Optional[str] = None,
):
    """Matches by team. Cached 5 minutes."""
    return await proxy(
        "/v3/matches/team",
        {"id": id, "page": page, "type": type, "lang": lang, "theme": theme, "time": time},
        TTL_SHORT,
    )


@app.get("/squads")
async def squads(
    id: str = Query(...),
    lang: Optional[str] = None,
    theme: Optional[str] = None,
):
    """Team squad/roster. Cached 24 hours."""
    return await proxy("/v2/squads", {"id": id, "lang": lang, "theme": theme}, TTL_DAY)


@app.get("/search")
async def search(
    query: str = Query(...),
    filter: Optional[str] = None,
    theme: Optional[str] = None,
):
    """Search teams, players, leagues. Cached 5 minutes."""
    return await proxy("/v3/search", {"query": query, "filter": filter, "theme": theme}, TTL_SHORT)


@app.get("/top-stats")
async def top_stats(
    id: str = Query(...),
    lang: Optional[str] = None,
    theme: Optional[str] = None,
    time: Optional[str] = None,
    competitors: Optional[str] = None,
):
    """Top scorers / assists / stats. Cached 1 hour."""
    return await proxy(
        "/v2/top-stats",
        {"id": id, "lang": lang, "theme": theme, "time": time, "competitors": competitors},
        TTL_LONG,
    )


@app.get("/transfers")
async def transfers(
    id: str = Query(...),
    lang: Optional[str] = None,
):
    """Transfer news by team/player. Cached 1 hour."""
    return await proxy("/v2/transfers", {"id": id, "lang": lang}, TTL_LONG)


@app.get("/winners")
async def winners(
    id: str = Query(...),
    lang: Optional[str] = None,
    time: Optional[str] = None,
    theme: Optional[str] = None,
):
    """Tournament winners history. Cached 24 hours."""
    return await proxy("/v2/winners", {"id": id, "lang": lang, "time": time, "theme": theme}, TTL_DAY)


# ─── Health check ─────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok"}
