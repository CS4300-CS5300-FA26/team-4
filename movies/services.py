import requests
from django.conf import settings

TMDB_BASE = "https://api.themoviedb.org/3"
POSTER_BASE = "https://image.tmdb.org/t/p/w500"
CAST_LIMIT = 10

#Ask TMDB for one movie and return the raw anser
def fetch_movie(tmdb_id):
    if not settings.TMDB_API_KEY:
        raise RuntimeError("TMDB_API_KEY is not set. See the README.")
    response = requests.get(f"{TMDB_BASE}/movie/{tmdb_id}",
        params = {"api_key": settings.TMDB_API_KEY, "append_to_response": "credits"}, #asks TMDB to include the cast in the same answer
        timeout = 10,
    )
    
    response.raise_for_status()     #turns 401/404/500 into an error we can catch
    return response.json()

#pulls the "name" out of each dict in a list, ignoring anything odd.
def _names(items, limit=None):
    if not isinstance(items, list):
        return []
    names = [i["name"] for i in items if isinstance(i, dict) and i.get("name")]
    return names[:limit] if limit else names

#Turn raw answer into dictionary, uses .get() so a missing field never crashes the page.
def build_movie_context(data):
    poster_path = data.get("poster_path")
    rating = data.get("vote_average")
    credits = data.get("credits")
    cast = credits.get("cast") if isinstance(credits, dict) else []
    return {
        "title": data.get("title"),
        "release_year": (data.get("release_date") or "")[:4],
        "overview": data.get("overview"),
        "poster_url": f"https://image.tmdb.org/t/p/w500{data['poster_path']}" if data.get("poster_path") else None,
        "genres": _names(data.get("genres")), 
        "cast": _names(cast, CAST_LIMIT),
        "rating": round(rating, 1) if rating is not None else None,
        "where_to_watch": [],   #will fill in later
    }