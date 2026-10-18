from django.urls import path
from . import views

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path(
        'watchlist/add/<int:movie_id>/',
        views.add_to_watchlist,
        name='add_to_watchlist'
    ),
]