from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from urllib.parse import urlsplit

from movies.models import Movie, WatchlistItem


class HomeWatchlistTest(TestCase):
    def setUp(self):
        User = get_user_model()

        self.user_one = User.objects.create_user(
            username="userone",
            password="testpass123"
        )

        self.user_two = User.objects.create_user(
            username="usertwo",
            password="testpass123"
        )

        self.movie_one = Movie.objects.create(
            title="Interstellar",
            overview="Space exploration."
        )

        self.movie_two = Movie.objects.create(
            title="The Matrix",
            overview="A simulated reality."
        )

    def test_user_sees_movies_in_their_own_watchlist(self):
        WatchlistItem.objects.create(
            user=self.user_one,
            movie=self.movie_one
        )

        self.client.login(
            username="userone",
            password="testpass123"
        )

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Interstellar")

    def test_user_does_not_see_another_users_watchlist_movies(self):
        WatchlistItem.objects.create(
            user=self.user_two,
            movie=self.movie_two
        )

        self.client.login(
            username="userone",
            password="testpass123"
        )

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "The Matrix")

    def test_each_user_only_sees_their_own_movies(self):
        WatchlistItem.objects.create(
            user=self.user_one,
            movie=self.movie_one
        )

        WatchlistItem.objects.create(
            user=self.user_two,
            movie=self.movie_two
        )

        self.client.login(
            username="userone",
            password="testpass123"
        )

        response = self.client.get(reverse("home"))

        self.assertContains(response, "Interstellar")
        self.assertNotContains(response, "The Matrix")

    def test_empty_watchlist_message_is_shown(self):
        self.client.login(
            username="userone",
            password="testpass123"
        )

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Your watchlist is empty"
        )

# check that the email is saved in database
class RegistrationEmailTests(TestCase):
    def test_registration_saves_submitted_email(self):
        email = "persist@example.com"

        response = self.client.post(
            reverse("register"),
            {
                "username": "persistuser",
                "email": email,
                "password1": "StrongTestPassword2026!",
                "password2": "StrongTestPassword2026!",
            },
        )
        
        self.assertEqual(response.status_code, 302)

        User = get_user_model()
        user = User.objects.get(username="persistuser")
        
        self.assertEqual(user.email, email)

class AccountAuthTests(TestCase):
    def test_register_view_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password1': 'SecurePassword123!',
                'password2': 'SecurePassword123!',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(get_user_model().objects.filter(username='newuser').exists())
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertRedirects(response, reverse('home'))

    def test_login_view_authenticates_existing_user(self):
        get_user_model().objects.create_user(
            username='existinguser',
            email='user@example.com',
            password='ValidPassword123!',
        )

        response = self.client.post(
            reverse('login'),
            {
                'username': 'existinguser',
                'password': 'ValidPassword123!',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.wsgi_request.user.username, 'existinguser')


class PasswordResetTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='resetuser',
            email='resetuser@example.com',
            password='OldPassword123!',
        )

    def test_password_reset_email_link_changes_password(self):
        response = self.client.post(
            reverse('password_reset'),
            {'email': self.user.email},
        )

        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])

        reset_url = next(
            line.strip()
            for line in mail.outbox[0].body.splitlines()
            if 'password-reset-confirm/' in line
        )
        response = self.client.get(urlsplit(reset_url).path, follow=True)
        self.assertContains(response, 'Enter new password')

        response = self.client.post(
            response.request['PATH_INFO'],
            {
                'new_password1': 'NewPassword456!',
                'new_password2': 'NewPassword456!',
            },
            follow=True,
        )

        self.assertContains(response, 'Password reset complete')
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword456!'))

    def test_unknown_email_does_not_send_reset_email(self):
        response = self.client.post(
            reverse('password_reset'),
            {'email': 'unknown@example.com'},
        )

        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(mail.outbox, [])

    def test_invalid_reset_token_does_not_change_password(self):
        response = self.client.get(
            reverse(
                'password_reset_confirm',
                kwargs={'uidb64': 'invalid', 'token': 'invalid'},
            )
        )

        self.assertContains(response, 'invalid or has expired')
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('OldPassword123!'))
