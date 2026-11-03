from behave import given, when, then
from behave.api.pending_step import StepNotImplementedError
from django.urls import reverse
from movies.models import Movie

# --- Search by title ---
@given('I am on the search page')
def step_on_search_page(context):
    raise StepNotImplementedError(
        'Waiting for the search page to be implemented'
    )

@given('search results are displayed')
def step_search_results_displayed(context):
    raise StepNotImplementedError(
        'Waiting for search results implementation'
    )

@when('I enter a movie or show title')
def step_enter_title(context):
    context.search_title = 'Inception'

@when('I submit the search')
def step_submit_search(context):
    # replace 'q' with the actual search input name
    context.response = context.test.client.get(
        context.search_url,
        {'q': context.search_title}
    )

@then('matching titles should be displayed')
def step_matching_titles_displayed(context):
    # verify actual TMDB search results
    assert context.response.status_code == 200
    assert 'Inception' in context.response.content.decode()

@then('each result should show its poster and basic information')
def step_results_show_poster_and_information(context):
    # update selectors/HTML checks after the template is created.
    html = context.response.content.decode()

    assert 'Inception' in html
    assert 'poster' in html.lower()

# --- Filter results by genre ---
@when('I select a genre filter')
def step_select_genre(context):
    context.filters = getattr(context, 'filters', {})
    context.filters['genre'] = 'Action'

# --- Filter results by release year ---
@when('I select a release year filter')
def step_select_year(context):
    context.filters = getattr(context, 'filters', {})
    context.filters['year'] = '2010'

# --- Filter results by streaming service ---
@when('I select a streaming service filter')
def step_select_streaming_service(context):
    context.filters = getattr(context, 'filters', {})
    context.filters['service'] = 'Netflix'

# --- Filter results by rating ---
@when('I select a rating filter')
def step_select_rating(context):
    context.filters = getattr(context, 'filters', {})
    context.filters['rating'] = '7'

@then('only titles matching the selected genre should be displayed')
def step_genre_results(context):
    raise NotImplementedError("Waiting for search page implementation")

@then('only titles matching the selected release year should be displayed')
def step_year_results(context):
    raise NotImplementedError("Waiting for search page implementation")

@then('only titles available on the selected streaming service should be displayed')
def step_streaming_results(context):
    raise NotImplementedError("Waiting for search page implementation")

@then('only titles matching the selected rating criteria should be displayed')
def step_rating_results(context):
    raise NotImplementedError("Waiting for search page implementation")

@then('only titles matching all selected filters should be displayed')
def step_multiple_filters(context):
    raise NotImplementedError("Waiting for search page implementation")