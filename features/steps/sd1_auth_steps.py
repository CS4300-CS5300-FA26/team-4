from behave import given, when, then
from django.contrib.auth.models import User
from django.urls import reverse
import uuid

# --- Registration Steps ---
@given('I am on the registration page')
def step_impl(context):
    context.response = context.test.client.get(reverse('register'))
    context.test.assertEqual(context.response.status_code, 200)

@when('I submit a valid username, email, and password')
def step_impl(context):
    unique_id = uuid.uuid4().hex[:8]

    context.username = f'newuser_{unique_id}'
    context.email = f'newuser_{unique_id}@example.com'

    form_data = {
        'username': context.username,
        'email': context.email,
        'password1': 'SecurePassword123!',
        'password2': 'SecurePassword123!'
    }

    context.response = context.test.client.post(
        reverse('register'),
        form_data,
        follow=True
    )

@then('a new account is created and I am taken to the home page')
def step_impl(context):
    # Verify the user exists in the database
    user_exists = User.objects.filter(
        username=context.username,
        email=context.email
    ).exists()

    context.test.assertTrue(user_exists)

    # Verify the new user is authenticated in the session
    user = User.objects.get(username=context.username)

    context.test.assertEqual(
        context.test.client.session['_auth_user_id'],
        str(user.pk)
    )

    # Verify redirection to home page
    context.test.assertRedirects(context.response, reverse('home'))

# --- Login Steps ---
@given('I have an existing account')
def step_impl(context):
    unique_id = uuid.uuid4().hex[:8]

    context.username = f'existinguser_{unique_id}'
    context.email = f'existinguser_{unique_id}@example.com'

    context.user = User.objects.create_user(
        username=context.username,
        email=context.email,
        password='ValidPassword123!'
    )

@given('I am on the login page')
def step_impl(context):
    context.response = context.test.client.get(reverse('login'))
    assert context.response.status_code == 200

@when('I submit my correct credentials')
def step_impl(context):
    form_data = {
        'username': context.username,
        'password': 'ValidPassword123!'
    }
    context.response = context.test.client.post(
        reverse('login'),
        form_data,
        follow=True
    )

@then('I am logged in and see my personalized home page')
def step_impl(context):
    # Check that the user is authenticated in the session
    session = context.test.client.session

    # Verify the session belongs to that same account
    context.test.assertEqual(session['_auth_user_id'], str(context.user.pk))

    # Verify the user was redirected to the home page
    context.test.assertRedirects(context.response, reverse('home'))

# --- Duplicate Registration ---
@given('an account already exists with my email')
def step_existing_email(context):
    unique_id = uuid.uuid4().hex[:8]

    context.email = f'duplicate_{unique_id}@example.com'

    context.user = User.objects.create_user(
        username=f'duplicateuser_{unique_id}',
        email=context.email,
        password='ValidPassword123!'
    )

@when('I register using the same email')
def step_register_duplicate(context):
    context.attempted_username = f'anotheruser_{uuid.uuid4().hex[:8]}'

    form_data = {
        'username': context.attempted_username,
        'email': context.email,
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
    context.test.assertContains(
        context.response,
        "An account with this email already exists."
    )

@then('the duplicate account should not be created')
def step_duplicate_not_created(context):
    context.test.assertFalse(
        User.objects.filter(
            username=context.attempted_username
        ).exists()
    )

    context.test.assertEqual(
        User.objects.filter(email=context.email).count(),
        1
    )

# --- Invalid Login Credentials ---
@when('I log in with an incorrect password')
def step_incorrect_password(context):
    form_data = {
        'username': context.username,
        'password': 'WrongPassword123!'
    }

    context.response = context.test.client.post(
        reverse('login'),
        form_data,
        follow=True
    )
    
@then('I should see an invalid login error')
def step_invalid_login_error(context):
    context.test.assertContains(
        context.response,
        'Please enter a correct username and password'
    )

@then('I should not be logged in')
def step_not_logged_in(context):
    # Verify the session does not contain an authenticated user.
    context.test.assertNotIn(
        '_auth_user_id',
        context.test.client.session
    )
