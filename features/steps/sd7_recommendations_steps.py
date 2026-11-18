from behave import given, when, then
from django.utils import timezone
from django.urls import reverse
from unittest.mock import patch
from movies.models import Movie, WatchlistItem

# helper function
def create_sd7_movie(context, title, tmdb_id, watched=False, rating=None):
    movie = Movie.objects.create(
        title=title,
        tmdb_id=tmdb_id,
        overview='A movie created for SD-7 testing.',
        release_year=2024
    )

    if not hasattr(context, 'sd7_created_movie_ids'):
        context.sd7_created_movie_ids = []

    context.sd7_created_movie_ids.append(movie.pk)

    WatchlistItem.objects.create(
        user=context.user,
        movie=movie,
        watched=watched,
        personal_rating=rating,
        watched_at=timezone.now() if watched else None
    )

    return movie

# --- Mock TMDB recommendation responses ---
def mock_recommendations():
    return {
        'results': [
            {
                'id': 801,
                'title': 'SD7 Recommended Movie One',
                'release_date': '2023-05-12',
                'poster_path': '/sd7-one.jpg',
                'vote_average': 8.2
            },
            {
                'id': 802,
                'title': 'SD7 Recommended Movie Two',
                'release_date': '2022-08-20',
                'poster_path': '/sd7-two.jpg',
                'vote_average': 7.5
            }
        ]
    }

# --- Recommendations are displayed based on watchlist or viewing history ---
@given('I have titles in my watchlist or viewing history')
def add_watchlist_history(context):
    context.sd7_seed_movie = create_sd7_movie(
        context,
        'SD7 Watched Seed Movie',
        701,
        watched=True,
        rating=9
    )

@when('I open the Recommendations page')
def open_recommendations(context):
    context.tmdb_patcher = patch(
        'movies.services._get',
        return_value=mock_recommendations()
    )
    context.tmdb_patcher.start()
    context.add_cleanup(context.tmdb_patcher.stop)

    context.response = context.test.client.get(
        reverse('personalized_recommendations')
    )

@then('I should see a list of recommended titles')
def verify_recommendations(context):
    context.test.assertEqual(context.response.status_code, 200)

    data = context.response.json()

    context.test.assertTrue(data['has_history'])
    context.test.assertGreater(len(data['movies']), 0)

@then('each recommendation should display a title')
def verify_recommendation_titles(context):
    data = context.response.json()

    for movie in data['movies']:
        context.test.assertTrue(movie['title'].strip())

@then('each recommendation should have accurate movie or show information')
def verify_recommendation_information(context):
    data = context.response.json()

    first_movie = data['movies'][0]

    context.test.assertEqual(
        first_movie['tmdb_id'],
        801
    )
    context.test.assertEqual(
        first_movie['title'],
        'SD7 Recommended Movie One'
    )
    context.test.assertEqual(
        first_movie['release_year'],
        '2023'
    )
    context.test.assertEqual(
        first_movie['rating'],
        8.2
    )
    context.test.assertTrue(first_movie['detail_url'])
    context.test.assertTrue(first_movie['add_url'])

# --- Recommendations load without errors when I have rated titles ---
@given('I have rated a movie or show')
def rate_movie(context):
    context.sd7_rated_movie = create_sd7_movie(
        context,
        'SD7 Rated Movie',
        703,
        watched=True,
        rating=9
    )

@then('the recommendations page should load successfully')
def verify_recommendations_load(context):
    context.test.assertEqual(context.response.status_code, 200)

@then('I should see recommended titles without errors')
def verify_recommendations_no_errors(context):
    data = context.response.json()

    context.test.assertTrue(data['has_history'])
    context.test.assertTrue(data['movies'])

    for movie in data['movies']:
        context.test.assertTrue(movie['title'])
        context.test.assertTrue(movie['detail_url'])

# --- Recommended for You section appears on the home page ---
@given('I have watched and rated several titles')
def create_watched_rated_titles(context):
    context.sd7_rated_movies = [
        create_sd7_movie(
            context, 'SD7 Action Movie', 704,
            watched=True, rating=10
        ),
        create_sd7_movie(
            context, 'SD7 Drama Movie', 705,
            watched=True, rating=8
        ),
        create_sd7_movie(
            context, 'SD7 Comedy Movie', 706,
            watched=True, rating=7
        ),
    ]

@when('I open the Home page')
def open_home_for_recommendations(context):
    context.trending_patcher = patch(
        'movies.views.fetch_trending_movies',
        return_value={'results': []}
    )
    context.trending_patcher.start()
    context.add_cleanup(context.trending_patcher.stop)

    context.response = context.test.client.get(reverse('movie_list'))

@then('I should see a Recommended for You section')
def verify_recommended_section(context):
    context.test.assertEqual(context.response.status_code, 200)

    context.test.assertContains(
        context.response,
        'Recommended for You'
    )

@then('the section should contain recommended titles')
def verify_recommended_section_titles(context):
    context.test.assertContains(
        context.response,
        'SD7 Recommended Movie One'
    )