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
    
    # might need to change
    with patch(
        'movies.views.fetch_popular_movies',
        return_value=context.popular_movies,
        create=True
    ):
        context.response = context.test.client.get(context.home_url)

    context.test.assertEqual(context.response.status_code, 200)

# --- Popular titles are displayed when the home page loads ---
@then('I should see a Popular section')
def verify_popular_section(context):
    context.test.assertContains(context.response, 'Popular') # might need to change

@then('I should see a list of currently popular titles')
def verify_popular_titles(context):
    context.test.assertContains(context.response, 'popular-movie') # might need to change

# --- Popular row displays at least 10 titles with posters ---
@then('the Popular row should contain at least 10 titles')
def verify_popular_count(context):
    raise NotImplementedError("Waiting for Popular row implementation")

@then('each popular title should have a poster')
def verify_popular_posters(context):
    raise NotImplementedError("Waiting for poster implementation")

@then('each popular title should have a title displayed')
def verify_popular_title_names(context):
    raise NotImplementedError("Waiting for title implementation")

# --- Selecting a popular title opens its details page ---
@when('I select a popular title')
def select_popular_title(context):
    raise NotImplementedError("Waiting for popular title selection implementation")

@then("I should be taken to that title's details page")
def verify_popular_detail_page(context):
    raise NotImplementedError("Waiting for movie detail navigation")

@then("I should see the selected title's details")
def verify_selected_title_details(context):
    raise NotImplementedError("Waiting for movie detail implementation")