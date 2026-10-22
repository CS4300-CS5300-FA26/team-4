import logging
import requests

from django.http import Http404, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, render

from .models import Movie, WatchlistItem
from .services import build_movie_context, fetch_movie


logger = logging.getLogger(__name__)


# Query all movies from the database and render them in the movie_list.html template.
def movie_list(request):
    movies = Movie.objects.all()
    return render(request, 'movies/movie_list.html', {'movies': movies})


def add_to_watchlist(request, movie_id):
    if not request.user.is_authenticated:
        return JsonResponse(
            {'error': 'Authentication required.'},
            status=401
        )

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    movie = get_object_or_404(Movie, id=movie_id)

    watchlist_item, created = WatchlistItem.objects.get_or_create(
        user=request.user,
        movie=movie
    )

    if not created:
        return JsonResponse(
            {'message': 'Movie is already in your watchlist.'},
            status=200
        )

    return JsonResponse(
        {'message': 'Movie added to your watchlist.'},
        status=201
    )


# Show one title's details, pulled live from TMDB
def movie_detail(request, tmdb_id):
    try:
        data = fetch_movie(tmdb_id)
    except RuntimeError:
        logger.error(
            "TMDB_API_KEY is not configured; cannot load movie %s",
            tmdb_id
        )
        return render(
            request,
            'movies/movie_detail.html',
            {'error': True},
            status=503
        )
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else None

        if status == 404:
            raise Http404("That movie was not found on TMDB.")

        if status in (401, 403):
            logger.error(
                "TMDB rejected the API key (HTTP %s)",
                status
            )
            return render(
                request,
                'movies/movie_detail.html',
                {'error': True},
                status=503
            )

        return render(
            request,
            'movies/movie_detail.html',
            {'error': True},
            status=502
        )

    except requests.RequestException:
        return render(
            request,
            'movies/movie_detail.html',
            {'error': True},
            status=502
        )

    saved_movie = Movie.objects.filter(tmdb_id=tmdb_id).first()

    return render(
        request,
        'movies/movie_detail.html',
        {
            'movie': build_movie_context(data),
            'saved_movie': saved_movie,
        }
    )
