from behave import given, when, then
from behave.api.pending_step import StepNotImplementedError
from django.urls import reverse
from unittest.mock import patch

SAMPLE_RESULTS = {
    "page": 1,
    "total_pages": 1,
    "total_results": 1,
    "results": [
        {
            "id": 27205,
            "title": "Inception",
            "release_date": "2010-07-16",
            "poster_path": "/inception.jpg",
            "vote_average": 8.4,
            "vote_count": 10000,
            "genre_ids": [28],
        }
    ],
}

# (helper function) submit a search while replacing the external TMDB request with sample data
def submit_search(context, params):
    with patch(
        "movies.services._get",
        return_value=SAMPLE_RESULTS
    ) as api_mock:

        context.response = context.test.client.get(
            context.search_url,
            params
        )

    context.api_mock = api_mock

# --- Search by title ---
@given('I am on the search page')
def step_on_search_page(context):
    context.search_url = reverse('movie_search')
    context.filters = {}
    context.search_title = 'Inception'

@given('search results are displayed')
def step_search_results_displayed(context):
    submit_search(context, {'query': 'Inception'})

    assert context.response.status_code == 200
    assert 'Inception' in context.response.content.decode()

    context.filters = {}

@when('I enter a movie or show title')
def step_enter_title(context):
    context.search_title = 'Inception'

@when('I submit the search')
def step_submit_search(context):
    submit_search(
        context,
        {'query': context.search_title}
    )

@then('matching titles should be displayed')
def step_matching_titles_displayed(context):
    html = context.response.content.decode()

    assert context.response.status_code == 200
    assert 'Inception' in html

    # confirm the search service received the title
    context.api_mock.assert_called_once()

    path, params = context.api_mock.call_args.args

    assert path == '/search/movie'
    assert params['query'] == 'Inception'

@then('each result should show its poster and basic information')
def step_results_show_poster_and_information(context):
    html = context.response.content.decode()

    assert 'Inception' in html
    assert 'Poster for Inception' in html
    assert 'inception.jpg' in html
    assert '2010' in html
    assert '8.4' in html

# --- Filter results by genre ---
@when('I select a genre filter')
def step_select_genre(context):
    context.filters['genre'] = 'action'

@then('only titles matching the selected genre should be displayed')
def step_genre_results(context):
    submit_search(context, context.filters)

    html = context.response.content.decode()

    assert context.response.status_code == 200
    assert 'Inception' in html

    path, params = context.api_mock.call_args.args

    assert path == '/discover/movie'
    assert params['with_genres'] == 28

# --- Filter results by release year ---
@when('I select a release year filter')
def step_select_year(context):
    context.filters['year'] = '2010'

@then('only titles matching the selected release year should be displayed')
def step_year_results(context):
    submit_search(context, context.filters)

    html = context.response.content.decode()

    assert context.response.status_code == 200
    assert 'Inception' in html

    path, params = context.api_mock.call_args.args

    assert path == '/discover/movie'
    assert params['primary_release_year'] == '2010'

# --- Filter results by streaming service ---
@when('I select a streaming service filter')
def step_select_streaming_service(context):
    context.filters['service'] = 'Netflix'

@then('only titles available on the selected streaming service should be displayed')
def step_streaming_results(context):
    raise NotImplementedError("Waiting for search page implementation")

# --- Filter results by rating ---
@when('I select a rating filter')
def step_select_rating(context):
    context.filters['min_rating'] = '7'

@then('only titles matching the selected rating criteria should be displayed')
def step_rating_results(context):
    submit_search(context, context.filters)

    html = context.response.content.decode()

    assert context.response.status_code == 200
    assert 'Inception' in html

    path, params = context.api_mock.call_args.args

    assert path == '/discover/movie'
    assert params['vote_average.gte'] == 7.0

# --- multiple filters ---
@then('only titles matching all selected filters should be displayed')
def step_multiple_filters(context):
    submit_search(context, context.filters)

    html = context.response.content.decode()

    assert context.response.status_code == 200
    assert 'Inception' in html

    path, params = context.api_mock.call_args.args

    assert path == '/discover/movie'
    assert params['with_genres'] == 28
    assert params['primary_release_year'] == '2010'
    assert params['vote_average.gte'] == 7.0