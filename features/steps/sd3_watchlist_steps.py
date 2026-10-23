from behave import given, when, then
from django.contrib.auth.models import User
from django.urls import reverse
from movies.models import Movie, WatchlistItem

# --- Add a title to my watchlist --- 
@given('I am logged in')
def step_logged_in(context):
    context.user = User.objects.create_user(
        username='sd3user',
        email='sd3user@example.com',
        password='TestPassword123!'
    )

    context.test.client.force_login(context.user)

@given('a movie exists that is not in my watchlist')
def step_movie_not_in_watchlist(context):
    context.movie = Movie.objects.create(
        title='SD3 Test Movie',
        overview='A movie for watchlist testing.',
        release_year=2024
    )

@when('I add the movie to my watchlist')
def step_add_movie(context):
    context.response = context.test.client.post(
        reverse('add_to_watchlist', args=[context.movie.pk])
    )

@then('the movie should appear in my watchlist')
def step_movie_appears(context):
    context.test.assertEqual(context.response.status_code, 201)

    context.test.assertEqual(
        WatchlistItem.objects.filter(
            user=context.user,
            movie=context.movie
        ).count(),
        1
    )

@then('the movie should be saved to my account')
def step_movie_saved_to_account(context):
    item = WatchlistItem.objects.get(
        user=context.user,
        movie=context.movie
    )

    context.test.assertEqual(item.user_id, context.user.pk)
    context.test.assertEqual(item.movie_id, context.movie.pk)

# --- Prevent duplicate watchlist entries --- 
@given('a movie is already in my watchlist')
def step_movie_already_in_watchlist(context):
    context.movie = Movie.objects.create(
        title='SD3 Duplicate Test Movie',
        overview='A movie for duplicate testing.',
        release_year=2023
    )

    WatchlistItem.objects.create(
        user=context.user,
        movie=context.movie
    )

@when('I add the same movie again')
def step_add_same_movie_again(context):
    context.response = context.test.client.post(
        reverse('add_to_watchlist', args=[context.movie.pk])
    )

@then('the movie should appear only once in my watchlist')
def step_movie_only_once(context):
    context.test.assertEqual(context.response.status_code, 200)

    context.test.assertEqual(
        WatchlistItem.objects.filter(
            user=context.user,
            movie=context.movie
        ).count(),
        1
    )

@then('I should see a message that the movie is already on my list')
def step_duplicate_message(context):
    context.test.assertEqual(
        context.response.json().get('message'),
        'Movie is already in your watchlist.'
    )