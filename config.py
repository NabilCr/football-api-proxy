import os
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY: str = os.getenv("RAPIDAPI_KEY", "")
RAPIDAPI_HOST: str = os.getenv("RAPIDAPI_HOST", "football-api-7.p.rapidapi.com")
RAPIDAPI_BASE_URL: str = os.getenv(
    "RAPIDAPI_BASE_URL", "https://football-api-7.p.rapidapi.com/api"
)
POSTS_BASE_URL: str = os.getenv(
    "POSTS_BASE_URL", "https://footballapi7.codechno.com/api"
)

RAPIDAPI_HEADERS: dict = {
    "x-rapidapi-host": RAPIDAPI_HOST,
    "x-rapidapi-key": RAPIDAPI_KEY,
}

# Cache TTL values (in seconds)
TTL_LIVE = 60          # live matches / match details
TTL_SHORT = 300        # 5 min  — matches by league/team, search
TTL_MEDIUM = 1800      # 30 min — highlights, statistics, posts
TTL_LONG = 3600        # 1 hr   — standings, h2h, top stats, transfers
TTL_DAY = 86400        # 24 hrs — countries, player, squads, winners
