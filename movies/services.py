import requests
from django.conf import settings

#TMDB identifies genres by number. These are TMDB's movie genre ids.
GENRE_IDS = {
    "action": 28, "adventure": 12, "animation": 16, "comedy": 35, "crime": 80, 
    "documentary": 99, "drama": 18, "family": 10751, "fantasy": 14,
    "history": 36, "horror": 27, "music": 10402, "mystery": 9648, 
    "romance": 10749, "science fiction": 878, "thriller": 53, "war": 10752, "western": 37,
}

TMDB_BASE = "https://api.themoviedb.org/3"
POSTER_BASE = "https://image.tmdb.org/t/p/w500"
CAST_LIMIT = 10
WATCH_REGION = 'US' #Steaming availability differs by country. We only show US results for now 
MIN_VOTES = 50  # ignores movies with a handful of votes, so rating mean something

#-- Movie Details ---------------------------------------------------------------------------
#Ask TMDB for one movie and return the raw anser
def fetch_movie(tmdb_id):
    if not settings.TMDB_API_KEY:
        raise RuntimeError("TMDB_API_KEY is not set. See the README.")
    response = requests.get(f"{TMDB_BASE}/movie/{tmdb_id}",
        params = {"api_key": settings.TMDB_API_KEY, "append_to_response": "credits,watch/providers"}, #asks TMDB to include the cast in the same answer
        timeout = 10,
    )
    
    response.raise_for_status()     #turns 401/404/500 into an error we can catch
    return response.json()

#pulls the "name" out of each dict in a list, ignoring anything odd.
def _names(items, limit=None, key="name"):
    if not isinstance(items, list):
        return []
    names = [i[key] for i in items if isinstance(i, dict) and i.get(key)]
    return names[:limit] if limit else names

#Names of subscription (flatrate) services for WATCH_REGION, or [] if none
def _providers(block):
    if not isinstance(block, dict):
        return []
    results = block.get('results')
    region = results.get(WATCH_REGION) if isinstance(results, dict) else None
    if not isinstance(region, dict):
        return[]
    return _names(region.get('flatrate'), key="provider_name")

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
        "where_to_watch": _providers(data.get("watch/providers")),   
    }

# -- Search & filter ------------------------------------------------

# A 4-digit year as a string, or None if it isn't one
def _clean_year(year):
    text = str(year or "").strip()
    return text if len(text) == 4 and text.isdigit() else None

# A rating between 0 and 10, or None if it isn't one
def _clean_rating(rating):
    try:
        value = float(rating)
    except (TypeError, ValueError):
        return None 
    return value if 0 <= value <= 10 else None

#A TMDB genre id for a genre name like "Drama", or None if unknown
def _clean_genre(genre):
    return GENRE_IDS.get(str(genre or "").strip().lower())

#Call TMDB with key. Same failure behavior as fetch_movie
def _get(path, params):
    if not settings.TMDB_API_KEY:
        raise RuntimeError("TMDB_API_KEY is not set. See the README")
    response = requests.get(
        f"{TMDB_BASE}{path}", params={"api_key": settings.TMDB_API_KEY, **params}, timeout=10,
    )
    response.raise_for_status()
    return response.json()
    
#Find movies by title and/or genre, year and minimum rating.
def search_movies(query="", genre=None, year=None, min_rating=None, page=1):
    query = (query or "").strip()
    genre_id = _clean_genre(genre)
    year = _clean_year(year)
    min_rating = _clean_rating(min_rating)

    if query:
        params = {"query": query, "page": page}
        if year:
            params["primary_release_year"] = year
        data = _get("/search/movie", params)
        results = data.get("results")
        results = results if isinstance(results, list) else []
        if genre_id:
            results = [m for m in results if isinstance(m, dict)
                    and genre_id in (m.get("genre_ids") or [])]
        if min_rating is not None:
            results = [m for m in results if isinstance(m, dict)
                    and (m.get("vote_average") or 0) >= min_rating]
        return {**data, "results": results}

    if not (genre_id or year or min_rating is not None):
        return {"page": 1, "results": [], "total_pages": 0, "total_results": 0}
    
    params = {"page": page, "sort_by": "popularity.desc", "vote_count.gte": MIN_VOTES}
    if genre_id:
        params["with_genres"] = genre_id
    if year:
        params["primary_release_year"] = year
    if min_rating is not None:
        params["vote_average.gte"] = min_rating
    return _get("/discover/movie", params)

#Turn TMDB's search reply into simple dicts the Search page can loop over
def build_search_results(data):
    results = data.get("results") if isinstance(data, dict) else None
    if not isinstance(results, list):
        return[]
    movies = []
    for item in results:
        if not isinstance(item, dict) or not item.get("id"):
            continue
        poster_path = item.get("poster_path")
        movies.append({
            "tmdb_id": item["id"],
            "title": item.get("title") or "",
            "release_year": (item.get("release_date") or "")[:4],
            "poster_url": f"{POSTER_BASE}{poster_path}" if poster_path else None,
            "rating": item.get("vote_average"),
        })
    return movies