from django.urls import path

from . import views


urlpatterns = [
    path(
        '',
        views.movie_list,
        name='movie_list'
    ),

    path(
        'watchlist/add/<int:movie_id>/',
        views.add_to_watchlist,
        name='add_to_watchlist'
    ),

    path(
        'watchlist/update/<int:movie_id>/',
        views.update_watchlist_item,
        name='update_watchlist_item'
    ),

    path(
        'movies/<int:tmdb_id>/',
        views.movie_detail,
        name='movie_detail'
    ),
]