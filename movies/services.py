import math
from collections import Counter

import requests
from django.conf import settings

from .models import WatchlistItem


# TMDB identifies genres by number.
GENRE_IDS = {
    "action": 28,
    "adventure": 12,
    "animation": 16,
    "comedy": 35,
    "crime": 80,
    "documentary": 99,
    "drama": 18,
    "family": 10751,
    "fantasy": 14,
    "history": 36,
    "horror": 27,
    "music": 10402,
    "mystery": 9648,
    "romance": 10749,
    "science fiction": 878,
    "thriller": 53,
    "war": 10752,
    "western": 37,
}


# Streaming services offered in the search filter.
PROVIDER_IDS = {
    "Netflix": 8,
    "Hulu": 15,
    "Amazon Prime Video": 9,
    "Disney+": 337,
    "HBO Max": 1899,
    "Apple TV": 350,
    "Paramount+": "2303|2616",
    "Peacock": "386|387",
}

_PROVIDERS_BY_LOWERCASE = {
    name.lower(): provider_id
    for name, provider_id in PROVIDER_IDS.items()
}


TMDB_BASE = "https://api.themoviedb.org/3"
POSTER_BASE = "https://image.tmdb.org/t/p/w500"
CAST_LIMIT = 10
WATCH_REGION = "US"
MIN_VOTES = 50
MAX_PAGE = 500


# -------------------------------------------------------------------
# Movie details
# -------------------------------------------------------------------

# Ask TMDB for one movie and return the raw response.
def fetch_movie(tmdb_id):
    if not settings.TMDB_API_KEY:
        raise RuntimeError(
            "TMDB_API_KEY is not set. See the README."
        )

    response = requests.get(
        f"{TMDB_BASE}/movie/{tmdb_id}",
        params={
            "api_key": settings.TMDB_API_KEY,
            "append_to_response": "credits,watch/providers",
        },
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


# Pull names out of a list of TMDB dictionaries.
def _names(items, limit=None, key="name"):
    if not isinstance(items, list):
        return []

    names = [
        item[key]
        for item in items
        if isinstance(item, dict) and item.get(key)
    ]

    return names[:limit] if limit else names


# Get subscription streaming providers for the US.
def _providers(block):
    if not isinstance(block, dict):
        return []

    results = block.get("results")

    region = (
        results.get(WATCH_REGION)
        if isinstance(results, dict)
        else None
    )

    if not isinstance(region, dict):
        return []

    return _names(
        region.get("flatrate"),
        key="provider_name",
    )


# Convert TMDB movie data into the format used by our templates.
def build_movie_context(data):
    rating = data.get("vote_average")

    credits = data.get("credits")

    cast = (
        credits.get("cast")
        if isinstance(credits, dict)
        else []
    )

    poster_path = data.get("poster_path")

    return {
        "title": data.get("title"),
        "release_year": (
            data.get("release_date") or ""
        )[:4],
        "overview": data.get("overview"),
        "poster_url": (
            f"{POSTER_BASE}{poster_path}"
            if poster_path
            else None
        ),
        "genres": _names(
            data.get("genres")
        ),
        "cast": _names(
            cast,
            CAST_LIMIT,
        ),
        "rating": (
            round(rating, 1)
            if rating is not None
            else None
        ),
        "where_to_watch": _providers(
            data.get("watch/providers")
        ),
    }


# -------------------------------------------------------------------
# Search and filter
# -------------------------------------------------------------------

# Return a valid four-digit year or None.
def _clean_year(year):
    text = str(year or "").strip()

    return (
        text
        if len(text) == 4 and text.isdigit()
        else None
    )


# Return a valid rating between 0 and 10 or None.
def _clean_rating(rating):
    try:
        value = float(rating)

    except (TypeError, ValueError):
        return None

    return (
        value
        if math.isfinite(value)
        and 0 <= value <= 10
        else None
    )


# Return a valid number from TMDB or 0.
def _number(value):
    if (
        isinstance(value, bool)
        or not isinstance(
            value,
            (int, float),
        )
    ):
        return 0

    return (
        value
        if math.isfinite(value)
        else 0
    )


# Return the year part of a TMDB release date.
def _year_of(release_date):
    return (
        release_date[:4]
        if isinstance(release_date, str)
        else ""
    )


# Convert a provider name into its TMDB provider ID.
def _clean_provider(provider):
    return _PROVIDERS_BY_LOWERCASE.get(
        str(provider or "")
        .strip()
        .lower()
    )


# Convert a genre name into its TMDB genre ID.
def _clean_genre(genre):
    return GENRE_IDS.get(
        str(genre or "")
        .strip()
        .lower()
    )


# Keep page numbers inside TMDB's allowed range.
def _clean_page(page):
    try:
        number = int(page)

    except (TypeError, ValueError):
        return 1

    return (
        min(number, MAX_PAGE)
        if number >= 1
        else 1
    )


# Make a general TMDB GET request.
def _get(path, params):
    if not settings.TMDB_API_KEY:
        raise RuntimeError(
            "TMDB_API_KEY is not set. See the README"
        )

    response = requests.get(
        f"{TMDB_BASE}{path}",
        params={
            "api_key": settings.TMDB_API_KEY,
            **params,
        },
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


# Get this week's trending movies.
def fetch_trending_movies():
    return _get(
        "/trending/movie/week",
        {
            "language": "en-US",
        },
    )


# Find movies using the selected search filters.
def search_movies(
    query="",
    genre=None,
    year=None,
    min_rating=None,
    page=1,
    provider=None,
):
    query = (query or "").strip()

    genre_id = _clean_genre(genre)
    year = _clean_year(year)
    min_rating = _clean_rating(min_rating)
    page = _clean_page(page)
    provider_id = _clean_provider(provider)

    # Title searches use TMDB's search endpoint.
    if query:
        params = {
            "query": query,
            "page": page,
        }

        if year:
            params["primary_release_year"] = year

        data = _get(
            "/search/movie",
            params,
        )

        if not isinstance(data, dict):
            data = {}

        results = data.get("results")

        results = (
            results
            if isinstance(results, list)
            else []
        )

        results = [
            movie
            for movie in results
            if isinstance(movie, dict)
        ]

        if genre_id:
            results = [
                movie
                for movie in results
                if isinstance(
                    movie.get("genre_ids"),
                    list,
                )
                and genre_id
                in movie["genre_ids"]
            ]

        if min_rating is not None:
            results = [
                movie
                for movie in results
                if _number(
                    movie.get("vote_average")
                ) >= min_rating
                and _number(
                    movie.get("vote_count")
                ) >= MIN_VOTES
            ]

        filtered = bool(
            genre_id
            or min_rating is not None
        )

        return {
            **data,
            "results": results,
            "filtered": filtered,
            "page_total_results": len(
                results
            ),
            "provider_ignored": bool(
                provider_id
            ),
        }

    # If no filters were entered, return no results.
    if not (
        genre_id
        or year
        or min_rating is not None
        or provider_id
    ):
        return {
            "page": 1,
            "results": [],
            "total_pages": 0,
            "total_results": 0,
        }

    # Filter-only searches use TMDB's discover endpoint.
    params = {
        "page": page,
        "sort_by": "popularity.desc",
        "vote_count.gte": MIN_VOTES,
    }

    if genre_id:
        params["with_genres"] = genre_id

    if year:
        params["primary_release_year"] = year

    if min_rating is not None:
        params["vote_average.gte"] = (
            min_rating
        )

    if provider_id:
        params["with_watch_providers"] = (
            provider_id
        )
        params["watch_region"] = (
            WATCH_REGION
        )
        params[
            "with_watch_monetization_types"
        ] = "flatrate"

    return _get(
        "/discover/movie",
        params,
    )


# Convert TMDB search results into data used by our templates.
def build_search_results(data):
    results = (
        data.get("results")
        if isinstance(data, dict)
        else None
    )

    if not isinstance(results, list):
        return []

    movies = []

    for item in results:
        if (
            not isinstance(item, dict)
            or not item.get("id")
        ):
            continue

        poster_path = item.get(
            "poster_path"
        )

        movies.append({
            "tmdb_id": item["id"],
            "title": (
                item.get("title") or ""
            ),
            "release_year": _year_of(
                item.get("release_date")
            ),
            "poster_url": (
                f"{POSTER_BASE}{poster_path}"
                if poster_path
                else None
            ),
            "rating": item.get(
                "vote_average"
            ),
        })

    return movies


# -------------------------------------------------------------------
# Sprint 3 - Viewing statistics
# -------------------------------------------------------------------

# Count watched movies and determine the user's most-watched genres.
# Genres are fetched from TMDB because our Movie model does not store them.
def build_viewing_stats(user):
    watched_items = (
        WatchlistItem.objects
        .filter(
            user=user,
            watched=True,
        )
        .select_related("movie")
    )

    genre_counts = Counter()

    for item in watched_items:
        tmdb_id = item.movie.tmdb_id

        # Movies without a TMDB ID still count as watched,
        # but we cannot look up their genre.
        if not tmdb_id:
            continue

        try:
            movie_data = fetch_movie(
                tmdb_id
            )

        except (
            RuntimeError,
            requests.RequestException,
        ):
            continue

        genres = movie_data.get(
            "genres",
            [],
        )

        if not isinstance(genres, list):
            continue

        for genre in genres:
            if not isinstance(genre, dict):
                continue

            name = genre.get("name")

            if name:
                genre_counts[name] += 1

    genre_counts = [
        {
            "genre": name,
            "count": count,
        }
        for name, count
        in genre_counts.most_common()
    ]

    return {
        "total_watched":
            watched_items.count(),
        "genre_counts":
            genre_counts,
        "top_genre": (
            genre_counts[0]["genre"]
            if genre_counts
            else None
        ),
    }


# -------------------------------------------------------------------
# Sprint 3 - Recommendation history
# -------------------------------------------------------------------

# Return the user's highest-rated watched movies.
# Eleasia can use the TMDB IDs to request similar recommendations.
def get_highest_rated_history(
    user,
    limit=5,
):
    items = (
        WatchlistItem.objects
        .filter(
            user=user,
            watched=True,
            personal_rating__isnull=False,
        )
        .select_related("movie")
        .order_by(
            "-personal_rating",
            "-watched_at",
        )[:limit]
    )

    return [
        {
            "movie_id":
                item.movie.id,
            "tmdb_id":
                item.movie.tmdb_id,
            "title":
                item.movie.title,
            "personal_rating":
                item.personal_rating,
        }
        for item in items
    ]