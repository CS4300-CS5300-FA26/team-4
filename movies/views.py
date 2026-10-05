from django.shortcuts import render
from .models import Movie

# Query all movies from the database and render them in the movie_list.html template.
def movie_list(request):
    movies = Movie.objects.all()
    return render(request, 'movies/movie_list.html', {'movies': movies})