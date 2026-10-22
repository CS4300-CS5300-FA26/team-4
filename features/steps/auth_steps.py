from behave import given, when, then
from django.contrib.auth.models import User
from django.urls import reverse

# --- Registration Steps ---
@given('I am on the registration page')
def step_impl(context):
    context.response = context.test.client.get(reverse('register'))
    context.test.assertEqual(context.response.status_code, 200)

@when('I submit a valid username, email, and password')
def step_impl(context):
    form_data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password1': 'SecurePassword123!',
        'password2': 'SecurePassword123!'
    }
    context.response = context.test.client.post(reverse('register'), form_data, follow=True)

@then('a new account is created and I am taken to the home page')
def step_impl(context):
    # Verify the user exists in the database
    user_exists = User.objects.filter(username='newuser').exists()
    context.test.assertTrue(user_exists)

    # Verify the new user is authenticated in the session
    context.test.assertTrue(context.response.context['user'].is_authenticated)

    # Verify redirection to home page
    context.test.assertRedirects(context.response, reverse('home'))

# --- Login Steps ---
@given('I have an existing account')
def step_impl(context):
    context.user = User.objects.create_user(
        username='existinguser',
        email='user@example.com',
        password='ValidPassword123!'
    )

@given('I am on the login page')
def step_impl(context):
    context.response = context.test.client.get(reverse('login'))
    context.test.assertEqual(context.response.status_code, 200)

@when('I submit my correct credentials')
def step_impl(context):
    form_data = {
        'username': 'existinguser',
        'password': 'ValidPassword123!'
    }
    context.response = context.test.client.post(reverse('login'), form_data, follow=True)

@then('I am logged in and see my personalized home page')
def step_impl(context):
    # Check that the user is authenticated in the session
    logged_in_user = context.response.context['user']
    context.test.assertTrue(logged_in_user.is_authenticated)

    # Verify it is specifically the account used in this scenario.
    context.test.assertEqual(logged_in_user.username, 'existinguser')

    # Verify the session belongs to that same account.
    context.test.assertEqual(context.test.client.session['_auth_user_id'], str(context.user.pk))

    # Verify the user was redirected to the home page.
    context.test.assertRedirects(context.response, reverse('home'))

# --- Duplicate Registration ---
@given('an account already exists with my email')
def step_existing_email(context):
    context.user = User.objects.create_user(
        username='duplicateuser',
        email='duplicate@example.com',
        password='ValidPassword123!'
    )

@when('I register using the same email')
def step_register_duplicate(context):
    form_data = {
        'username': 'anotheruser',
        'email': 'duplicate@example.com',
        'password1': 'SecurePassword123!',
        'password2': 'SecurePassword123!'
    }

    context.response = context.test.client.post(
        reverse('register'),
        form_data,
        follow=True
    )

@then('I should see a duplicate email error')
def step_duplicate_email_error(context):
    form = context.response.context.get('form')

    context.test.assertIsNotNone(
        form,
        "Expected the registration form in the response."
    )

    context.test.assertIn(
        'email',
        form.errors,
        "Expected a validation error on the email field."
    )

@then('the duplicate account should not be created')
def step_duplicate_not_created(context):
    context.test.assertFalse(
        User.objects.filter(username='anotheruser').exists(),
        'A new account was created despite using an existing email.'
    )

    context.test.assertEqual(
        User.objects.filter(email='duplicate@example.com').count(),
        1,
        'The duplicate email should belong to exactly one account.'
    )

# --- Invalid Login Credentials ---
@when('I log in with an incorrect password')
def step_incorrect_password(context):
    form_data = {
        'username': 'existinguser',
        'password': 'WrongPassword123!'
    }

    context.response = context.test.client.post(
        reverse('login'),
        form_data,
        follow=True
    )
    
@then('I should see an invalid login error')
def step_invalid_login_error(context):
    # Make sure the login page returned a form.
    form = context.response.context.get('form')

    context.test.assertIsNotNone(
        form,
        "Expected the login form in the response."
    )

    # Invalid credentials should produce a form-level error.
    context.test.assertTrue(
        form.non_field_errors(),
        "Expected an invalid-credentials error on the login form."
    )

@then('I should not be logged in')
def step_not_logged_in(context):
    # Verify the session does not contain an authenticated user.
    context.test.assertNotIn(
        '_auth_user_id',
        context.test.client.session
    )
