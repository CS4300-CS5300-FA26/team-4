from behave import given, when, then
from django.urls import reverse
from django.core.cache import cache
from unittest.mock import patch
from movies.models import Movie, WatchlistItem

# helper function
def create_sd10_movie(context, title, tmdb_id):
    movie = Movie.objects.create(
        title=title,
        tmdb_id=tmdb_id
    )

    if not hasattr(context, 'sd10_created_movie_ids'):
        context.sd10_created_movie_ids = []

    context.sd10_created_movie_ids.append(movie.pk)

    return movie

# --- View total watched titles and genre statistics ---
@given('I have marked several titles as watched')
def create_watched_titles(context):
    # create three movies with TMDB IDs
    context.movie_one = create_sd10_movie(
        context, 'SD10 Movie One', 101
        )

    context.movie_two = create_sd10_movie(
        context, 'SD10 Movie Two', 102
        )

    context.unwatched_movie = create_sd10_movie(
        context, 'SD10 Unwatched Movie', 103
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

# --- View the statistics dashboard on the Watchlist page ---
@when('I open my Watchlist page')
def open_watchlist_page(context):
    context.response = context.test.client.get(
        reverse('home')
    )

@then('I should see the statistics dashboard')
def verify_statistics_dashboard(context):
    context.test.assertEqual(
        context.response.status_code,
        200
    )

    html = context.response.content.decode('utf-8')

    context.test.assertIn('id="profile"', html)
    context.test.assertIn('data-stats-url=', html)
    context.test.assertIn('data-stat="total_watched"', html)

@then('I should see the watched genre chart')
def verify_watched_genre_chart(context):
    html = context.response.content.decode('utf-8')

    context.test.assertIn('class="genre-chart"', html)
    context.test.assertIn(
        'aria-label="Watched movies by genre"',
        html
    )

@then('the dashboard styles and script should be included')
def verify_dashboard_assets(context):
    html = context.response.content.decode('utf-8')

    context.test.assertIn(
        '/static/movies/dashboard.css',
        html
    )

    context.test.assertIn(
        '/static/movies/dashboard.js',
        html
    )