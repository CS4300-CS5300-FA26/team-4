from unittest.mock import Mock, patch

import requests
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Movie, WatchlistItem
from .services import build_movie_context, fetch_movie


FAKE_TMDB = {
    "title": "Inception",
    "release_date": "2010-07-15",
    "overview": "A heist hidden inside a dream.",
    "poster_path": "/abc.jpg",
    "genres": [
        {"id": 28, "name": "Action"},
        {"id": 878, "name": "Science Fiction"}
    ],
    "vote_average": 8.373,
    "credits": {
        "cast": [
            {"name": "Leonardo DiCaprio"},
            {"name": "Elliot Page"}
        ]
    },
    "watch/providers": {"results": {
        "US": {"flatrate": [{"provider_name": "Netflix"},
        {"provider_name": "Max"}],
        "rent": [{"provider_name": "Apple TV"}]},
        "FR": {"flatrate": [{"provider_name": "Canal+"}]},
    }},
}


def fake_response(data=None, status=200):
    """A pretend reply from TMDB, so no test touches the real internet."""
    response = Mock()
    response.status_code = status
    response.json.return_value = data

    if status >= 400:
        response.raise_for_status.side_effect = requests.HTTPError(
            response=response
        )

    return response


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

        self.assertEqual(response.status_code, 401)

    def test_watchlist_rejects_get_request(self):
        response = self.client.get(
            reverse("add_to_watchlist", args=[self.movie.id])
        )

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response["Allow"], "POST")


@override_settings(TMDB_API_KEY="test-key")
class FetchMovieTest(TestCase):
    @patch("movies.services.requests.get")
    def test_sends_the_key_and_asks_for_cast(self, mock_get):
        mock_get.return_value = fake_response(FAKE_TMDB)

        result = fetch_movie(27205)

        self.assertEqual(result["title"], "Inception")

        args, kwargs = mock_get.call_args

        self.assertTrue(args[0].endswith("/movie/27205"))
        self.assertEqual(kwargs["params"]["api_key"], "test-key")
        self.assertIn(
            "credits",
            kwargs["params"]["append_to_response"]
        )
        self.assertIn("watch/providers", kwargs["params"]["append_to_response"])

    @override_settings(TMDB_API_KEY="")
    @patch("movies.services.requests.get")
    def test_missing_key_gives_a_clear_error(self, mock_get):
        with self.assertRaises(RuntimeError):
            fetch_movie(27205)

        mock_get.assert_not_called()

    @patch("movies.services.requests.get")
    def test_tmdb_rejecting_the_request_raises_an_error(self, mock_get):
        mock_get.return_value = fake_response(status=401)

        with self.assertRaises(requests.HTTPError):
            fetch_movie(27205)


PLAIN_STATIC = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage"
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
    },
}


@override_settings(STORAGES=PLAIN_STATIC)
class MovieDetailViewTest(TestCase):
    @patch("movies.views.fetch_movie", return_value=FAKE_TMDB)
    def test_detail_page_shows_title_cast_and_attribution(
        self,
        mock_fetch
    ):
        response = self.client.get(
            reverse("movie_detail", args=[27205])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Inception")
        self.assertContains(response, "Leonardo DiCaprio")
        self.assertContains(
            response,
            "not endorsed or certified by TMDB"
        )
        self.assertContains(response, "Where to Watch (US)")
        self.assertContains(response, "Netflix, Max")
        self.assertContains(response, "JustWatch")

        mock_fetch.assert_called_once_with(27205)

    @patch(
        "movies.views.fetch_movie",
        side_effect=requests.ConnectionError
    )
    def test_tmdb_being_down_shows_friendly_message(
        self,
        mock_fetch
    ):
        response = self.client.get(
            reverse("movie_detail", args=[27205])
        )

        self.assertEqual(response.status_code, 502)
        self.assertContains(
            response,
            "We couldn't reach the movie database",
            status_code=502
        )

    @override_settings(TMDB_API_KEY="")
    def test_missing_key_error_page_not_a_crash(self):
        with self.assertLogs("movies.views", level="ERROR"):
            response = self.client.get(
                reverse("movie_detail", args=[27205])
            )

        self.assertEqual(response.status_code, 503)
        self.assertContains(
            response,
            "unavailable",
            status_code=503
        )

    @patch(
        "movies.views.fetch_movie",
        side_effect=requests.HTTPError(
            response=Mock(status_code=404)
        )
    )
    def test_unknown_movie_returns_404(self, mock_fetch):
        response = self.client.get(
            reverse("movie_detail", args=[1])
        )

        self.assertEqual(response.status_code, 404)

    @patch(
        "movies.views.fetch_movie",
        side_effect=requests.HTTPError(
            response=Mock(status_code=401)
        )
    )
    def test_rejected_api_key_is_a_configuration_error(
        self,
        mock_fetch
    ):
        with self.assertLogs("movies.views", level="ERROR"):
            response = self.client.get(
                reverse("movie_detail", args=[27205])
            )

        self.assertEqual(response.status_code, 503)

    @patch(
        "movies.views.fetch_movie",
        side_effect=requests.HTTPError(
            response=Mock(status_code=500)
        )
    )
    def test_tmdb_server_error_is_a_502(self, mock_fetch):
        response = self.client.get(
            reverse("movie_detail", args=[27205])
        )

        self.assertEqual(response.status_code, 502)

    @patch(
        "movies.views.fetch_movie",
        return_value={
            "title": "Odd Movie",
            "genres": None,
            "credits": {
                "cast": [
                    None,
                    "oops",
                    {"name": None},
                    {"name": "Real Actor"}
                ]
            }
        }
    )
    def test_odd_tmdb_data_does_not_crash_the_page(
        self,
        mock_fetch
    ):
        response = self.client.get(
            reverse("movie_detail", args=[5])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Real Actor")


class BuildMovieContextTest(TestCase):
    def test_missing_or_wrong_shaped_fields_become_empty_lists(self):
        context = build_movie_context(
            {
                "genres": "Action",
                "credits": None
            }
        )

        self.assertEqual(context["genres"], [])
        self.assertEqual(context["cast"], [])
    
    def test_only_subscription_services_for_our_region_are_listed(self):
        context = build_movie_context(FAKE_TMDB)
        self.assertEqual(context["where_to_watch"], ["Netflix", "Max"])
        
    def test_missing_or_odd_provider_data_gives_an_empty_list(self):
        for odd in (None, "x", {}, {"results": None}, {"results": "oops"}, {"results": {"US": None}},
        {"results": {"US": {"flatrate": None}}} ):
            self.assertEqual(build_movie_context({"watch/providers": odd})["where_to_watch"], [])
