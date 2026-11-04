from django.conf import settings
from django.db import models
from django.db.models import Q


class Movie(models.Model):
    title = models.CharField(max_length=255)
    overview = models.TextField(blank=True)
    release_year = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    poster_url = models.URLField(blank=True)
    tmdb_id = models.PositiveIntegerField(
        unique=True,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


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

    watched = models.BooleanField(default=False)

    personal_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True
    )

    watched_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'movie'],
                name='unique_user_movie_watchlist'
            ),
            models.CheckConstraint(
                condition=(
                    Q(personal_rating__isnull=True)
                    | Q(
                        personal_rating__gte=1,
                        personal_rating__lte=10
                    )
                ),
                name='personal_rating_between_1_and_10'
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.movie}"