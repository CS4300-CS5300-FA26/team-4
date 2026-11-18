from django.urls import path
from . import views


urlpatterns = [

    path(
        '',
        views.movie_list,
        name='movie_list'
    ),
    
    path(
        'search/',
        views.movie_search,
        name='movie_search'
    ),

    path(
        'watchlist/add/tmdb/<int:tmdb_id>/',
        views.add_search_movie_to_watchlist,
        name='add_search_movie_to_watchlist',
    ),

    path(
        'watchlist/add/<int:movie_id>/',
        views.add_to_watchlist,
        name='add_to_watchlist'
    ),

    path(
        'watchlist/remove/<int:movie_id>/',
        views.remove_from_watchlist,
        name='remove_from_watchlist',
    ),

    path(
        'watchlist/update/<int:movie_id>/',
        views.update_watchlist_item,
        name='update_watchlist_item'
    ),

    # Sprint 3: viewing statistics.
    path(
        'stats/',
        views.viewing_stats,
        name='viewing_stats'
    ),

    # Sprint 3: highest-rated history for recommendations.
    path(
        'recommendations/',
        views.personalized_recommendations,
        name='personalized_recommendations',
    ),

    path(
        'recommendations/history/',
        views.recommendation_history,
        name='recommendation_history'
    ),

    path(
        'movies/<int:tmdb_id>/',
        views.movie_detail,
        name='movie_detail'
    ),

    path(
        'recommendations/browse/',
        views.recommendations_page,
        name='recommendations_page',
    ),
]
