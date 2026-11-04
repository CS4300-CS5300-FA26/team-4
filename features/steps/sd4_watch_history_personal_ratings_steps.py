from behave import given, when, then
from django.utils import timezone
from django.urls import reverse
from movies.models import Movie, WatchlistItem

# (helper function) create a movie and add it to the user's watchlist
def create_watchlist_movie(context, title):
    context.movie = Movie.objects.create(
        title=title,
        overview='A movie for SD-4 testing.',
        release_year=2024
    )

    context.watchlist_item = WatchlistItem.objects.create(
        user=context.user,
        movie=context.movie
    )

# --- Mark a watchlist title as watched ---
@given('a title is in my watchlist')
def step_title_in_watchlist(context):
    create_watchlist_movie(context, 'SD4 Watchlist Movie')

@given('a title is in my watchlist or search results')
def step_title_in_watchlist_or_search(context):
    context.watched_count_before = WatchlistItem.objects.filter(
        user=context.user,
        watched=True
    ).count()

    create_watchlist_movie(context, 'SD4 Rating Movie')


@given('a title is in my viewing history')
def step_title_in_history(context):
    context.movie = Movie.objects.create(
        title='SD4 History Movie',
        overview='A movie for history testing.',
        release_year=2024
    )

    context.watchlist_item = WatchlistItem.objects.create(
        user=context.user,
        movie=context.movie,
        watched=True,
        watched_at=timezone.now()
    )

@when('I select "Mark as watched"')
def step_select_mark_as_watched(context):
    context.response = context.test.client.post(
        reverse('update_watchlist_item', args=[context.movie.pk]),
        {'watched': 'true'}
    )

# --- Mark a title as watched and provide a rating ---
@when('I mark the title as watched')
def step_mark_title_as_watched(context):
    context.response = context.test.client.post(
        reverse('update_watchlist_item', args=[context.movie.pk]),
        {'watched': 'true'}
    )

@when('I select a personal rating')
def step_select_personal_rating(context):
    context.selected_rating = 8

# --- Rate a title in viewing history ---
@when('I save my rating')
def step_save_rating(context):
    context.response = context.test.client.post(
        reverse('update_watchlist_item', args=[context.movie.pk]),
        {'rating': str(context.selected_rating)}
    )

@when('I select "Rate this"')
def step_select_rate_this(context):
    context.rating_action_selected = True

@then('the title should be marked as watched')
def step_title_marked_watched(context):
    context.test.assertEqual(context.response.status_code, 200)

    item = WatchlistItem.objects.get(
        user=context.user,
        movie=context.movie
    )

    context.test.assertTrue(item.watched)
    context.test.assertIsNotNone(item.watched_at)

@then('the title should appear in my viewing history')
def step_title_in_viewing_history(context):
    item = WatchlistItem.objects.get(
        user=context.user,
        movie=context.movie
    )

    context.test.assertTrue(item.watched)

@then('my rating should be saved for the title')
def step_rating_saved(context):
    item = WatchlistItem.objects.get(
        user=context.user,
        movie=context.movie
    )

    context.test.assertEqual(
        item.personal_rating,
        context.selected_rating
    )

@then('my viewing statistics should be updated')
def step_statistics_updated(context):
    watched_count_after = WatchlistItem.objects.filter(
        user=context.user,
        watched=True
    ).count()

    context.test.assertGreater(
        watched_count_after,
        context.watched_count_before
    )

@then('the title should appear in my viewing history with my rating')
def step_history_shows_rating(context):
    item = WatchlistItem.objects.get(
        user=context.user,
        movie=context.movie
    )

    context.test.assertTrue(item.watched)
    context.test.assertIsNotNone(item.personal_rating)

@then('my saved rating should match the rating I selected')
def step_saved_rating_matches(context):
    item = WatchlistItem.objects.get(
        user=context.user,
        movie=context.movie
    )

    context.test.assertEqual(
        item.personal_rating,
        context.selected_rating
    )