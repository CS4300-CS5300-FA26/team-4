from behave import given, when, then
from django.urls import reverse
from django.core.cache import cache
from unittest.mock import patch
from movies.models import Movie, WatchlistItem

# --- View total watched titles and genre statistics ---
@given('I have marked several titles as watched')
def create_watched_titles(context):
    # create three movies with TMDB IDs
    context.movie_one = Movie.objects.create(
        title='SD10 Movie One',
        tmdb_id=101
    )

    context.movie_two = Movie.objects.create(
        title='SD10 Movie Two',
        tmdb_id=102
    )

    context.unwatched_movie = Movie.objects.create(
        title='SD10 Unwatched Movie',
        tmdb_id=103
    )

    # add two watched movies and one unwatched movie
    WatchlistItem.objects.create(
        user=context.user,
        movie=context.movie_one,
        watched=True
    )

    WatchlistItem.objects.create(
        user=context.user,
        movie=context.movie_two,
        watched=True
    )

    WatchlistItem.objects.create(
        user=context.user,
        movie=context.unwatched_movie,
        watched=False
    )

    # remove any cached genre data from an earlier test
    cache.delete_many([
        'movie_genres_101',
        'movie_genres_102',
        'movie_genres_103',
    ])

    # mock TMDB responses so the test does not need the internet
    patcher = patch(
        'movies.services.fetch_movie',
        side_effect=[
            {'genres': [
                {'name': 'Action'},
                {'name': 'Drama'},
            ]},
            {'genres': [
                {'name': 'Action'},
            ]},
        ]
    )

    patcher.start()
    context.add_cleanup(patcher.stop)

    context.expected_watched_count = 2

@when('I open the Statistics page')
def open_statistics(context):
    context.response = context.test.client.get(
        reverse('viewing_stats')
    )

@then('I should see my total number of watched titles')
def verify_watched_count(context):
    context.test.assertEqual(context.response.status_code, 200)

    data = context.response.json()

    context.test.assertEqual(
        data['total_watched'],
        context.expected_watched_count
    )

@then('I should see statistics about the genres I watch most')
def verify_genre_statistics(context):
    data = context.response.json()

    context.test.assertEqual(
        data['genre_counts'],
        [
            {'genre': 'Action', 'count': 2},
            {'genre': 'Drama', 'count': 1},
        ]
    )

    context.test.assertEqual(data['top_genre'], 'Action')

@then('my genre statistics should be returned as structured data')
def verify_genre_data_structure(context):
    data = context.response.json()

    context.test.assertIsInstance(data['genre_counts'], list)

    for genre in data['genre_counts']:
        context.test.assertIn('genre', genre)
        context.test.assertIn('count', genre)
        context.test.assertIsInstance(genre['count'], int)