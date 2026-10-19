from django.conf import settings
from django.db import models


# This model represents a movie in the personal movie watchlist application.
# It includes fields for the title, overview, release year, poster URL, TMDB ID,
# and the date the movie was added to the database.
# Movies are ordered alphabetically by title.
class Movie(models.Model):
    title = models.CharField(max_length=255)
    overview = models.TextField(blank=True)
    release_year = models.PositiveIntegerField(null=True, blank=True)
    poster_url = models.URLField(blank=True)
    tmdb_id = models.PositiveIntegerField(unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


# This model represents a movie saved to a user's personal watchlist.
# Each watchlist item belongs to one user and one movie.
class WatchlistItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'movie'],
                name='unique_user_movie_watchlist'
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.movie}"