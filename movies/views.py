import requests
import logging
from django.shortcuts import render
from django.http import Http404

from .models import Movie
from .services import fetch_movie, build_movie_context

logger = logging.getLogger(__name__)

# Query all movies from the database and render them in the movie_list.html template.
def movie_list(request):
    movies = Movie.objects.all()
    return render(request, 'movies/movie_list.html', {'movies': movies})

#Show one title's details, pulled live from TMDB
def movie_detail(request, tmdb_id):
    try:
        data = fetch_movie(tmdb_id)
    except RuntimeError:
        #Configuration problem, not a TMDB outage
        logger.error("TMDB_API_KEY is not configured; cannot load movie %s", tmdb_id)
        return render(request, 'movies/movie_detail.html', {'error': True}, status=503)
    except requests.RequestException:
        # Network problem, timeout, etc
        return render(request, 'movies/movie_detail.html', {'error': True}, status=502)
    return render(request, 'movies/movie_detail.html', {'movie': build_movie_context(data)})