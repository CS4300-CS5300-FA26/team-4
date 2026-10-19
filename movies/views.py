from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render

from .models import Movie, WatchlistItem


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