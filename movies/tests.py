from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Movie, WatchlistItem


class MovieListViewTest(TestCase):
    def test_saved_movie_appears_on_the_page(self):
        Movie.objects.create(
            title="Inception",
            overview="A heist in dreams."
        )

        response = self.client.get(reverse("movie_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Inception")
        self.assertContains(response, "A heist in dreams.")

    def test_empty_state_shown_when_no_movies_exist(self):
        response = self.client.get(reverse("movie_list"))

        self.assertContains(response, "No movies in the database yet")


class WatchlistTest(TestCase):
    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

        self.movie = Movie.objects.create(
            title="Interstellar",
            overview="Explorers travel through space."
        )

        self.client.login(
            username="testuser",
            password="testpass123"
        )

    def test_user_can_add_movie_to_watchlist(self):
        response = self.client.post(
            reverse("add_to_watchlist", args=[self.movie.id])
        )

        self.assertEqual(response.status_code, 201)

        self.assertTrue(
            WatchlistItem.objects.filter(
                user=self.user,
                movie=self.movie
            ).exists()
        )

    def test_duplicate_movie_is_not_added_twice(self):
        WatchlistItem.objects.create(
            user=self.user,
            movie=self.movie
        )

        response = self.client.post(
            reverse("add_to_watchlist", args=[self.movie.id])
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            WatchlistItem.objects.filter(
                user=self.user,
                movie=self.movie
            ).count(),
            1
        )

    def test_watchlist_requires_login(self):
        self.client.logout()

        response = self.client.post(
            reverse("add_to_watchlist", args=[self.movie.id])
        )

        self.assertEqual(response.status_code, 302)

    def test_watchlist_rejects_get_request(self):
        response = self.client.get(
            reverse("add_to_watchlist", args=[self.movie.id])
        )

        self.assertEqual(response.status_code, 405)