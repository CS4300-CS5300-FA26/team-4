from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

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
