from behave import given, when, then
from django.urls import reverse
from unittest.mock import patch

# helper function
def create_popular_movies():
    """Create mock TMDB popular movie results."""

    movies = []

    for movie_id in range(1, 11):
        movies.append({
            'id': movie_id,
            'title': f'SD6 Popular Movie {movie_id}',
            'overview': f'Test overview for movie {movie_id}.',
            'poster_path': f'/sd6-poster-{movie_id}.jpg',
            'release_date': '2025-01-01',
            'vote_average': 8.0,
        })

    return {
        'results': movies,
        'total_pages': 1,
    }

@given('I am on the Home page')
def visit_home_page(context):
    context.home_url = reverse('movie_list') # might need to change

@when('the page loads')
def page_loads(context):
    context.popular_movies = create_popular_movies()

    with patch(
        'movies.views.fetch_trending_movies',
        return_value=context.popular_movies
    ):
        context.response = context.test.client.get(context.home_url)

    context.test.assertEqual(context.response.status_code, 200)

# --- Popular titles are displayed when the home page loads ---
@then('I should see a Popular section')
def verify_popular_section(context):
    context.test.assertContains(context.response, 'Trending this week')

@then('I should see a list of currently popular titles')
def verify_popular_titles(context):
    context.test.assertContains(context.response, 'SD6 Popular Movie 1')

# --- Popular row displays at least 10 titles with posters ---
@then('the Popular row should contain at least 10 titles')
def verify_popular_count(context):
    html = context.response.content.decode()

    movie_count = html.count('<article class="movie">')

    context.test.assertGreaterEqual(
        movie_count,
        10,
        f"Expected at least 10 popular titles, but found {movie_count}."
    )

@then('each popular title should have a poster')
@then('each popular title should have a poster')
def verify_popular_posters(context):
    html = context.response.content.decode()

    poster_count = html.count('class="movie-thumbnail"')
    movie_count = html.count('<article class="movie">')

    context.test.assertEqual(
        poster_count,
        movie_count,
        f"Expected {movie_count} posters, but found {poster_count}."
    )

@then('each popular title should have a title displayed')
def verify_popular_title_names(context):
    html = context.response.content.decode()

    for movie in context.popular_movies['results']:
        title = movie['title']

        context.test.assertContains(
            context.response,
            title,
            msg_prefix=f"Movie title '{title}' was not displayed."
        )

# --- Selecting a popular title opens its details page ---
@when('I select a popular title')
def select_popular_title(context):
    first_movie = context.popular_movies['results'][0]

    context.selected_movie_id = first_movie['id']
    context.selected_movie_title = first_movie['title']

    detail_url = reverse(
        'movie_detail',
        args=[context.selected_movie_id]
    )

    # Confirm the selected movie has a details link on the Home page.
    context.test.assertContains(context.response, detail_url)

    context.tmdb_data = {
        'title': context.selected_movie_title,
        'release_date': first_movie['release_date'],
        'overview': first_movie['overview'],
        'poster_path': first_movie['poster_path'],
        'vote_average': first_movie['vote_average'],
        'genres': [{'id': 1, 'name': 'Adventure'}],
        'credits': {
            'cast': [{'name': 'SD6 Test Actor'}]
        },
    }

    with patch(
        'movies.views.fetch_movie',
        return_value=context.tmdb_data
    ):
        context.response = context.test.client.get(detail_url)

@then("I should be taken to that title's details page")
def verify_popular_detail_page(context):
    context.test.assertEqual(
        context.response.status_code,
        200
    )

@then("I should see the selected title's details")
def verify_selected_title_details(context):
    context.test.assertContains(
        context.response,
        context.selected_movie_title
    )

    context.test.assertContains(
        context.response,
        context.popular_movies['results'][0]['overview']
    )