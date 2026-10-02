from django.db import models

# Create your models here for the movies app. 
# This model represents a movie in the personal movie watchlist application. 
# It includes fields for the title, overview, release year, poster URL, TMDB ID, and 
# the date the movie was added to the watchlist. 
# The model also specifies that movies should be ordered by title when queried from the database.
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