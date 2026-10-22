from unittest.mock import patch
from behave import given, when, then
from django.urls import reverse

# --- View complete movie details ---
@given('a movie has poster, overview, cast, genres, ratings, and streaming information')
def step_movie_has_details(context):
    context.tmdb_id = 12345

    context.tmdb_data = {
        'title': 'SD9 Test Movie',
        'release_date': '2024-05-10',
        'overview': 'A test overview for the movie.',
        'poster_path': '/test-poster.jpg',
        'vote_average': 8.2,
        'genres': [
            {'id': 1, 'name': 'Adventure'},
            {'id': 2, 'name': 'Drama'},
        ],
        'credits': {
            'cast': [
                {'name': 'Test Actor'},
                {'name': 'Test Actress'},
            ]
        },
    }

@when('I open the movie details page')
def step_open_movie_details(context):
    with patch(
        'movies.views.fetch_movie',
        return_value=context.tmdb_data
    ):
        context.response = context.test.client.get(
            reverse('movie_detail', args=[context.tmdb_id])
        )

@then('I should see the movie poster')
def step_see_movie_poster(context):
    context.test.assertContains(
        context.response,
        'https://image.tmdb.org/t/p/w500/test-poster.jpg'
    )

@then('I should see the movie overview')
def step_see_movie_overview(context):
    context.test.assertContains(
        context.response,
        'A test overview for the movie.'
    )

@then('I should see the cast and genres')
def step_see_cast_and_genres(context):
    context.test.assertContains(context.response, 'Test Actor')
    context.test.assertContains(context.response, 'Test Actress')
    context.test.assertContains(context.response, 'Adventure')
    context.test.assertContains(context.response, 'Drama')

@then('I should see ratings and streaming information')
def step_see_ratings_and_streaming(context):
    context.test.assertContains(context.response, '8.2')
    context.test.assertContains(context.response, 'Where to Watch')
    context.test.assertContains(
        context.response,
        'Streaming information unavailable.'
    )

# --- Add a movie from its details page ---
@given('I am viewing a movie details page')
def step_viewing_movie_details(context):
    # Create a movie that can be added to the user's watchlist.
    from movies.models import Movie

    context.movie = Movie.objects.create(
        title='SD9 Test Movie',
        overview='A test overview for the movie.',
        release_year=2024,
        tmdb_id=12345,
    )

    context.tmdb_id = 12345
    context.tmdb_data = {
        'title': 'SD9 Test Movie',
        'release_date': '2024-05-10',
        'overview': 'A test overview for the movie.',
        'poster_path': '/test-poster.jpg',
        'vote_average': 8.2,
        'genres': [{'id': 1, 'name': 'Adventure'}],
        'credits': {'cast': [{'name': 'Test Actor'}]},
    }

    from unittest.mock import patch
    from django.urls import reverse

    with patch('movies.views.fetch_movie', return_value=context.tmdb_data):
        context.response = context.test.client.get(
            reverse('movie_detail', args=[context.tmdb_id])
        )

# --- Open movie details from different pages ---
@given('a movie is available from "{source}"')
def step_movie_available_from_source(context, source):
    from movies.models import Movie

    context.movie_source = source
    context.tmdb_id = 12345
    context.tmdb_data = {
        'title': 'SD9 Test Movie',
        'release_date': '2024-05-10',
        'overview': 'A test overview for the movie.',
        'poster_path': '/test-poster.jpg',
        'vote_average': 8.2,
        'genres': [{'id': 1, 'name': 'Adventure'}],
        'credits': {'cast': [{'name': 'Test Actor'}]},
    }

    context.movie = Movie.objects.create(
        title='SD9 Test Movie',
        overview='A test overview for the movie.',
        release_year=2024,
        tmdb_id=context.tmdb_id,
    )


@when('I select the movie')
def step_select_movie(context):
    from unittest.mock import patch
    from django.urls import reverse

    with patch('movies.views.fetch_movie', return_value=context.tmdb_data):
        context.response = context.test.client.get(
            reverse('movie_detail', args=[context.tmdb_id])
        )


@then('I should see its details page')
def step_see_movie_details_page(context):
    context.test.assertEqual(context.response.status_code, 200)
    context.test.assertContains(context.response, 'SD9 Test Movie')
    context.test.assertContains(context.response, 'A test overview for the movie.')