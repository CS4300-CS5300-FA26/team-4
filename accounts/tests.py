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