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
    context.test.assertTrue(context.response.context['user'].is_authenticated)
    context.test.assertRedirects(context.response, reverse('home'))