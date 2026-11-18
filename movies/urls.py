from django.urls import path

from . import views


urlpatterns = [

    # Home page with trending movies.
    path(
        "",
        views.movie_list,
        name="movie_list",
    ),

    # Search and filter movies.
    path(
        "search/",
        views.movie_search,
        name="movie_search",
    ),

    # Add a TMDB search result to the watchlist.
    path(
        "watchlist/add/tmdb/<int:tmdb_id>/",
        views.add_search_movie_to_watchlist,
        name="add_search_movie_to_watchlist",
    ),

    # Add a locally stored movie to the watchlist.
    path(
        "watchlist/add/<int:movie_id>/",
        views.add_to_watchlist,
        name="add_to_watchlist",
    ),

    # Remove a movie from the watchlist.
    path(
        "watchlist/remove/<int:movie_id>/",
        views.remove_from_watchlist,
        name="remove_from_watchlist",
    ),

    # Update watched status and personal rating.
    path(
        "watchlist/update/<int:movie_id>/",
        views.update_watchlist_item,
        name="update_watchlist_item",
    ),

    # Sprint 3: viewing statistics.
    path(
        "stats/",
        views.viewing_stats,
        name="viewing_stats",
    ),

    # Sprint 3: highest-rated history for recommendations.
    path(
        "recommendations/history/",
        views.recommendation_history,
        name="recommendation_history",
    ),

    # Individual TMDB movie details.
    path(
        "movies/<int:tmdb_id>/",
        views.movie_detail,
        name="movie_detail",
    ),
]