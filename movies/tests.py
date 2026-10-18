from unittest.mock import Mock, patch

import requests
from django.test import TestCase, override_settings
from django.urls import reverse
from .models import Movie

from .services import build_movie_context, fetch_movie
# Create your tests here.

FAKE_TMDB = {
    "title": "Inception",
    "release_date": "2010-07-15",
    "overview": "A heist hidden inside a dream.",
    "poster_path": "/abc.jpg",
    "genres": [{"id": 28, "name": "Action"}, {"id": 878, "name": "Science Fiction"}],
    "vote_average": 8.373,
    "credits": {"cast": [{"name": "Leonardo DiCaprio"}, {"name": "Elliot Page"}]},
}

def fake_response(data=None, status=200):
    """A pretend reply from TMDB, so no test touches the real internet."""
    response = Mock()
    response.status_code = status
    response.json.return_value = data
    if status >= 400:
        response.raise_for_status.side_effect = requests.HTTPError(response=response)
    return response

class MovieListViewTest(TestCase):
    def test_saved_movie_appears_on_the_page(self):
        Movie.objects.create(title="Inception", overview="A heist in dreams.")  #Test movie
        response = self.client.get(reverse("movie_list"))
        self.assertEqual(response.status_code, 200)         #tests if the page loaded successfully
        self.assertContains(response, "Inception")          #tests if movie is in page
        self.assertContains(response, "A heist in dreams.") 

    def test_empty_state_shown_when_no_movies_exist(self):      #tests if page runs correctly when no movies exists
        response = self.client.get(reverse("movie_list"))
        self.assertContains(response, "No movies in the database yet")

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
        self.assertIn("credits", kwargs["params"]["append_to_response"])
 
    @override_settings(TMDB_API_KEY="")
    @patch("movies.services.requests.get")
    def test_missing_key_gives_a_clear_error(self, mock_get):
        with self.assertRaises(RuntimeError):
            fetch_movie(27205)
        mock_get.assert_not_called()  # it must fail before contacting TMDB
 
    @patch("movies.services.requests.get")
    def test_tmdb_rejecting_the_request_raises_an_error(self, mock_get):
        mock_get.return_value = fake_response(status=401)
        with self.assertRaises(requests.HTTPError):
            fetch_movie(27205)

# The real settings use hashed static files, which need a collectstatic manifest.
# Tests don't run collectstatic, so use plain static storage while testing.
PLAIN_STATIC = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


@override_settings(STORAGES=PLAIN_STATIC)
class MovieDetailViewTest(TestCase):
    @patch("movies.views.fetch_movie", return_value=FAKE_TMDB)
    def test_detail_page_shows_title_cast_and_attribution(self, mock_fetch):
        response = self.client.get(reverse("movie_detail", args=[27205]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Inception")
        self.assertContains(response, "Leonardo DiCaprio")
        self.assertContains(response, "not endorsed or certified by TMDB")
        mock_fetch.assert_called_once_with(27205)
 
    @patch("movies.views.fetch_movie", side_effect=requests.ConnectionError)
    def test_tmdb_being_down_shows_friendly_message(self, mock_fetch):
        response = self.client.get(reverse("movie_detail", args=[27205]))
        self.assertEqual(response.status_code, 502)
        self.assertContains(response, "We couldn't reach the movie database", status_code=502)

    @override_settings(TMDB_API_KEY="")
    def test_missing_key_error_page_not_a_crash(self):
        with self.assertLogs("movies.views", level="ERROR"):
            response = self.client.get(reverse("movie_detail", args=[27205]))
        self.assertEqual(response.status_code, 503)
        self.assertContains(response, "unavailable", status_code=503)