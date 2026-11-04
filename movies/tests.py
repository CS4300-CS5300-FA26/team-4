from unittest.mock import Mock, patch

import requests
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Movie, WatchlistItem
from .services import (
    build_movie_context,
    fetch_movie,
    build_search_results,
    search_movies,
)


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
    "watch/providers": {
        "results": {
            "US": {
                "flatrate": [
                    {"provider_name": "Netflix"},
                    {"provider_name": "Max"}
                ],
                "rent": [
                    {"provider_name": "Apple TV"}
                ]
            },
            "FR": {
                "flatrate": [
                    {"provider_name": "Canal+"}
                ]
            },
        }
    },
}


# What TMDB's search/discover endpoints send back, trimmed down.
FAKE_SEARCH = {
    "page": 1,
    "total_pages": 1,
    "total_results": 3,
    "results": [
        {
            "id": 27205,
            "title": "Inception",
            "release_date": "2010-07-15",
            "poster_path": "/a.jpg",
            "vote_average": 8.4,
            "vote_count": 9000,
            "genre_ids": [28, 878]
        },
        {
            "id": 1,
            "title": "Inception Rip-off",
            "release_date": "2012-01-01",
            "poster_path": None,
            "vote_average": 4.2,
            "vote_count": 300,
            "genre_ids": [18]
        },
        {
            "id": 2,
            "title": "Inception Documentary",
            "release_date": "",
            "poster_path": "/b.jpg",
            "vote_average": 7.0,
            "vote_count": 400,
            "genre_ids": [99]
        },
    ],
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

        self.assertContains(
            response,
            "No movies in the database yet"
        )


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
            reverse(
                "add_to_watchlist",
                args=[self.movie.id]
            )
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
            reverse(
                "add_to_watchlist",
                args=[self.movie.id]
            )
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
            reverse(
                "add_to_watchlist",
                args=[self.movie.id]
            )
        )

        self.assertEqual(response.status_code, 401)

    def test_watchlist_rejects_get_request(self):
        response = self.client.get(
            reverse(
                "add_to_watchlist",
                args=[self.movie.id]
            )
        )

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response["Allow"], "POST")


class WatchHistoryRatingTest(TestCase):
    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username="historyuser",
            password="testpass123"
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            password="testpass123"
        )

        self.movie = Movie.objects.create(
            title="The Dark Knight",
            overview="Batman faces the Joker."
        )

        self.item = WatchlistItem.objects.create(
            user=self.user,
            movie=self.movie
        )

        self.client.login(
            username="historyuser",
            password="testpass123"
        )

    def test_user_can_mark_movie_as_watched(self):
        response = self.client.post(
            reverse(
                "update_watchlist_item",
                args=[self.movie.id]
            ),
            {
                "watched": "true"
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.item.refresh_from_db()

        self.assertTrue(
            self.item.watched
        )

        self.assertIsNotNone(
            self.item.watched_at
        )

    def test_user_can_mark_movie_as_unwatched(self):
        self.item.watched = True
        self.item.watched_at = timezone.now()
        self.item.save()

        response = self.client.post(
            reverse(
                "update_watchlist_item",
                args=[self.movie.id]
            ),
            {
                "watched": "false"
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.item.refresh_from_db()

        self.assertFalse(
            self.item.watched
        )

        self.assertIsNone(
            self.item.watched_at
        )

    def test_user_can_rate_movie(self):
        response = self.client.post(
            reverse(
                "update_watchlist_item",
                args=[self.movie.id]
            ),
            {
                "rating": "8"
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.item.refresh_from_db()

        self.assertEqual(
            self.item.personal_rating,
            8
        )

    def test_invalid_rating_is_rejected(self):
        response = self.client.post(
            reverse(
                "update_watchlist_item",
                args=[self.movie.id]
            ),
            {
                "rating": "15"
            }
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.item.refresh_from_db()

        self.assertIsNone(
            self.item.personal_rating
        )

    def test_non_numeric_rating_is_rejected(self):
        response = self.client.post(
            reverse(
                "update_watchlist_item",
                args=[self.movie.id]
            ),
            {
                "rating": "great"
            }
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.item.refresh_from_db()

        self.assertIsNone(
            self.item.personal_rating
        )

    def test_user_cannot_update_another_users_item(self):
        other_movie = Movie.objects.create(
            title="Alien",
            overview="A space horror movie."
        )

        WatchlistItem.objects.create(
            user=self.other_user,
            movie=other_movie
        )

        response = self.client.post(
            reverse(
                "update_watchlist_item",
                args=[other_movie.id]
            ),
            {
                "watched": "true"
            }
        )

        self.assertEqual(
            response.status_code,
            404
        )

        other_item = WatchlistItem.objects.get(
            user=self.other_user,
            movie=other_movie
        )

        self.assertFalse(
            other_item.watched
        )

    def test_update_requires_login(self):
        self.client.logout()

        response = self.client.post(
            reverse(
                "update_watchlist_item",
                args=[self.movie.id]
            ),
            {
                "watched": "true"
            }
        )

        self.assertEqual(
            response.status_code,
            401
        )

    def test_update_rejects_get_request(self):
        response = self.client.get(
            reverse(
                "update_watchlist_item",
                args=[self.movie.id]
            )
        )

        self.assertEqual(
            response.status_code,
            405
        )

        self.assertEqual(
            response["Allow"],
            "POST"
        )


@override_settings(TMDB_API_KEY="test-key")
class FetchMovieTest(TestCase):
    @patch("movies.services.requests.get")
    def test_sends_the_key_and_asks_for_cast(self, mock_get):
        mock_get.return_value = fake_response(FAKE_TMDB)

        result = fetch_movie(27205)

        self.assertEqual(result["title"], "Inception")

        args, kwargs = mock_get.call_args

        self.assertTrue(
            args[0].endswith("/movie/27205")
        )
        self.assertEqual(
            kwargs["params"]["api_key"],
            "test-key"
        )
        self.assertIn(
            "credits",
            kwargs["params"]["append_to_response"]
        )
        self.assertIn(
            "watch/providers",
            kwargs["params"]["append_to_response"]
        )

    @override_settings(TMDB_API_KEY="")
    @patch("movies.services.requests.get")
    def test_missing_key_gives_a_clear_error(
        self,
        mock_get
    ):
        with self.assertRaises(RuntimeError):
            fetch_movie(27205)

        mock_get.assert_not_called()

    @patch("movies.services.requests.get")
    def test_tmdb_rejecting_the_request_raises_an_error(
        self,
        mock_get
    ):
        mock_get.return_value = fake_response(status=401)

        with self.assertRaises(requests.HTTPError):
            fetch_movie(27205)


PLAIN_STATIC = {
    "default": {
        "BACKEND":
        "django.core.files.storage.FileSystemStorage"
    },
    "staticfiles": {
        "BACKEND":
        "django.contrib.staticfiles.storage.StaticFilesStorage"
    },
}


@override_settings(STORAGES=PLAIN_STATIC)
class MovieDetailViewTest(TestCase):
    @patch(
        "movies.views.fetch_movie",
        return_value=FAKE_TMDB
    )
    def test_detail_page_shows_title_cast_and_attribution(
        self,
        mock_fetch
    ):
        response = self.client.get(
            reverse(
                "movie_detail",
                args=[27205]
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Inception")
        self.assertContains(
            response,
            "Leonardo DiCaprio"
        )
        self.assertContains(
            response,
            "not endorsed or certified by TMDB"
        )
        self.assertContains(
            response,
            "Where to Watch (US)"
        )
        self.assertContains(
            response,
            "Netflix, Max"
        )
        self.assertContains(
            response,
            "JustWatch"
        )

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
            reverse(
                "movie_detail",
                args=[27205]
            )
        )

        self.assertEqual(
            response.status_code,
            502
        )
        self.assertContains(
            response,
            "We couldn't reach the movie database",
            status_code=502
        )

    @override_settings(TMDB_API_KEY="")
    def test_missing_key_error_page_not_a_crash(self):
        with self.assertLogs(
            "movies.views",
            level="ERROR"
        ):
            response = self.client.get(
                reverse(
                    "movie_detail",
                    args=[27205]
                )
            )

        self.assertEqual(
            response.status_code,
            503
        )
        self.assertContains(
            response,
            "unavailable",
            status_code=503
        )

    @patch(
        "movies.views.fetch_movie",
        side_effect=requests.HTTPError(
            response=Mock(
                status_code=404
            )
        )
    )
    def test_unknown_movie_returns_404(
        self,
        mock_fetch
    ):
        response = self.client.get(
            reverse(
                "movie_detail",
                args=[1]
            )
        )

        self.assertEqual(
            response.status_code,
            404
        )

    @patch(
        "movies.views.fetch_movie",
        side_effect=requests.HTTPError(
            response=Mock(
                status_code=401
            )
        )
    )
    def test_rejected_api_key_is_a_configuration_error(
        self,
        mock_fetch
    ):
        with self.assertLogs(
            "movies.views",
            level="ERROR"
        ):
            response = self.client.get(
                reverse(
                    "movie_detail",
                    args=[27205]
                )
            )

        self.assertEqual(
            response.status_code,
            503
        )

    @patch(
        "movies.views.fetch_movie",
        side_effect=requests.HTTPError(
            response=Mock(
                status_code=500
            )
        )
    )
    def test_tmdb_server_error_is_a_502(
        self,
        mock_fetch
    ):
        response = self.client.get(
            reverse(
                "movie_detail",
                args=[27205]
            )
        )

        self.assertEqual(
            response.status_code,
            502
        )

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
            reverse(
                "movie_detail",
                args=[5]
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )
        self.assertContains(
            response,
            "Real Actor"
        )


class BuildMovieContextTest(TestCase):
    def test_missing_or_wrong_shaped_fields_become_empty_lists(
        self
    ):
        context = build_movie_context(
            {
                "genres": "Action",
                "credits": None
            }
        )

        self.assertEqual(
            context["genres"],
            []
        )
        self.assertEqual(
            context["cast"],
            []
        )

    def test_only_subscription_services_for_our_region_are_listed(
        self
    ):
        context = build_movie_context(
            FAKE_TMDB
        )

        self.assertEqual(
            context["where_to_watch"],
            ["Netflix", "Max"]
        )

    def test_missing_or_odd_provider_data_gives_an_empty_list(
        self
    ):
        odd_values = (
            None,
            "x",
            {},
            {"results": None},
            {"results": "oops"},
            {
                "results": {
                    "US": None
                }
            },
            {
                "results": {
                    "US": {
                        "flatrate": None
                    }
                }
            },
        )

        for odd in odd_values:
            self.assertEqual(
                build_movie_context(
                    {
                        "watch/providers": odd
                    }
                )["where_to_watch"],
                []
            )


@override_settings(TMDB_API_KEY="test-key")
class SearchMoviesTest(TestCase):
    @patch("movies.services.requests.get")
    def test_title_search_uses_the_search_endpoint(
        self,
        mock_get
    ):
        mock_get.return_value = fake_response(
            FAKE_SEARCH
        )

        search_movies(
            query="  Inception "
        )

        args, kwargs = mock_get.call_args

        self.assertTrue(
            args[0].endswith(
                "/search/movie"
            )
        )

        self.assertEqual(
            kwargs["params"]["query"],
            "Inception"
        )

        self.assertEqual(
            kwargs["params"]["api_key"],
            "test-key"
        )

        self.assertEqual(
            kwargs["timeout"],
            10
        )

    @patch("movies.services.requests.get")
    def test_title_search_passes_the_year_to_tmdb(
        self,
        mock_get
    ):
        mock_get.return_value = fake_response(
            FAKE_SEARCH
        )

        search_movies(
            query="Inception",
            year="2010"
        )

        self.assertEqual(
            mock_get.call_args.kwargs[
                "params"
            ]["primary_release_year"],
            "2010"
        )

    @patch("movies.services.requests.get")
    def test_title_search_filters_genre_and_rating_ourselves(
        self,
        mock_get
    ):
        mock_get.return_value = fake_response(
            FAKE_SEARCH
        )

        by_genre = search_movies(
            query="Inception",
            genre="Drama"
        )

        self.assertEqual(
            [
                movie["id"]
                for movie in by_genre["results"]
            ],
            [1]
        )

        by_rating = search_movies(
            query="Inception",
            min_rating=7
        )

        self.assertEqual(
            [
                movie["id"]
                for movie in by_rating["results"]
            ],
            [27205, 2]
        )

    @patch("movies.services.requests.get")
    def test_filters_without_a_title_use_the_discover_endpoint(
        self,
        mock_get
    ):
        mock_get.return_value = fake_response(
            FAKE_SEARCH
        )

        search_movies(
            genre="Science Fiction",
            year="2010",
            min_rating="7.5"
        )

        args, kwargs = mock_get.call_args

        self.assertTrue(
            args[0].endswith(
                "/discover/movie"
            )
        )

        params = kwargs["params"]

        self.assertEqual(
            params["with_genres"],
            878
        )
        self.assertEqual(
            params["primary_release_year"],
            "2010"
        )
        self.assertEqual(
            params["vote_average.gte"],
            7.5
        )
        self.assertEqual(
            params["vote_count.gte"],
            50
        )

    @patch("movies.services.requests.get")
    def test_nothing_to_search_for_does_not_call_tmdb(
        self,
        mock_get
    ):
        blank_searches = (
            {},
            {"query": "   "},
            {
                "genre": "nonsense",
                "year": "20x",
                "min_rating": "abc"
            }
        )

        for blank in blank_searches:
            self.assertEqual(
                search_movies(
                    **blank
                )["results"],
                []
            )

        mock_get.assert_not_called()

    @patch("movies.services.requests.get")
    def test_invalid_filters_are_ignored_not_sent(
        self,
        mock_get
    ):
        mock_get.return_value = fake_response(
            FAKE_SEARCH
        )

        search_movies(
            query="x",
            genre="nonsense",
            year="99",
            min_rating="11"
        )

        params = (
            mock_get.call_args.kwargs[
                "params"
            ]
        )

        self.assertNotIn(
            "primary_release_year",
            params
        )

        self.assertEqual(
            search_movies(
                query="x",
                min_rating="11"
            )["results"],
            FAKE_SEARCH["results"]
        )

    @override_settings(TMDB_API_KEY="")
    @patch("movies.services.requests.get")
    def test_missing_key_gives_a_clear_error(
        self,
        mock_get
    ):
        with self.assertRaises(
            RuntimeError
        ):
            search_movies(
                query="Inception"
            )

        mock_get.assert_not_called()

    @patch("movies.services.requests.get")
    def test_tmdb_error_raises(
        self,
        mock_get
    ):
        mock_get.return_value = fake_response(
            status=500
        )

        with self.assertRaises(
            requests.HTTPError
        ):
            search_movies(
                query="Inception"
            )

    @patch("movies.services.requests.get")
    def test_odd_search_data_does_not_crash(
        self,
        mock_get
    ):
        mock_get.return_value = fake_response(
            {
                "results": [
                    None,
                    "x",
                    {
                        "genre_ids": None,
                        "id": 3
                    }
                ]
            }
        )

        self.assertEqual(
            search_movies(
                query="x",
                genre="Drama"
            )["results"],
            []
        )

        mock_get.return_value = fake_response(
            {
                "results": "oops"
            }
        )

        self.assertEqual(
            search_movies(
                query="x",
                min_rating=5
            )["results"],
            []
        )

    @patch("movies.services.requests.get")
    def test_filtered_title_search_says_so_and_counts_this_pages_matches(
        self,
        mock_get
    ):
        mock_get.return_value = fake_response(
            FAKE_SEARCH
        )

        filtered = search_movies(
            query="Inception",
            genre="Drama"
        )

        self.assertTrue(
            filtered["filtered"]
        )
        self.assertEqual(
            filtered["page_total_results"],
            1
        )
        self.assertEqual(
            filtered["total_results"],
            3
        )

        plain = search_movies(
            query="Inception"
        )

        self.assertFalse(
            plain["filtered"]
        )
        self.assertEqual(
            plain["page_total_results"],
            3
        )

    @patch("movies.services.requests.get")
    def test_page_is_forced_to_a_valid_number(
        self,
        mock_get
    ):
        mock_get.return_value = fake_response(
            FAKE_SEARCH
        )

        cases = (
            (3, 3),
            ("2", 2),
            (0, 1),
            (-5, 1),
            ("abc", 1),
            (None, 1),
            (99999, 500),
        )

        for given, sent in cases:
            search_movies(
                query="x",
                page=given
            )

            self.assertEqual(
                mock_get.call_args.kwargs[
                    "params"
                ]["page"],
                sent
            )

    @patch("movies.services.requests.get")
    def test_reply_that_is_not_a_dictionary_gives_no_results(
        self,
        mock_get
    ):
        for odd in (
            [],
            ["x"],
            None,
            "oops"
        ):
            mock_get.return_value = (
                fake_response(odd)
            )

            self.assertEqual(
                search_movies(
                    query="x"
                )["results"],
                []
            )

            self.assertEqual(
                search_movies(
                    query="x",
                    genre="Drama"
                )["results"],
                []
            )

    @patch("movies.services.requests.get")
    def test_odd_result_fields_are_skipped_not_crashed_on(
        self,
        mock_get
    ):
        good = {
            "id": 1,
            "title": "Good",
            "vote_average": 8,
            "vote_count": 500,
            "genre_ids": [18]
        }

        odd = [
            {
                "id": 2,
                "vote_average": "8.0",
                "vote_count": 500,
                "genre_ids": [18]
            },
            {
                "id": 3,
                "vote_average": 8,
                "vote_count": "500",
                "genre_ids": [18]
            },
            {
                "id": 4,
                "vote_average": float("nan"),
                "vote_count": 500,
                "genre_ids": [18]
            },
            {
                "id": 5,
                "vote_average": True,
                "vote_count": 500,
                "genre_ids": [18]
            },
            {
                "id": 6,
                "vote_average": 8,
                "vote_count": 500,
                "genre_ids": 18
            },
            {
                "id": 7,
                "vote_average": 8,
                "vote_count": 500,
                "genre_ids": "18"
            },
        ]

        mock_get.return_value = fake_response(
            {
                "results": odd + [good]
            }
        )

        by_rating = search_movies(
            query="x",
            min_rating=7
        )

        self.assertEqual(
            [
                movie["id"]
                for movie
                in by_rating["results"]
            ],
            [6, 7, 1]
        )

        by_genre = search_movies(
            query="x",
            genre="Drama"
        )

        self.assertEqual(
            [
                movie["id"]
                for movie
                in by_genre["results"]
            ],
            [2, 3, 4, 5, 1]
        )


class BuildSearchResultsTest(TestCase):
    def test_results_become_simple_dicts(self):
        movies = build_search_results(
            FAKE_SEARCH
        )

        self.assertEqual(
            movies[0],
            {
                "tmdb_id": 27205,
                "title": "Inception",
                "release_year": "2010",
                "poster_url":
                "https://image.tmdb.org/t/p/w500/a.jpg",
                "rating": 8.4
            }
        )

    def test_missing_poster_and_date_are_handled(
        self
    ):
        movies = build_search_results(
            FAKE_SEARCH
        )

        self.assertIsNone(
            movies[1]["poster_url"]
        )

        self.assertEqual(
            movies[2]["release_year"],
            ""
        )

    def test_odd_data_gives_an_empty_list(
        self
    ):
        odd_values = (
            None,
            "x",
            {},
            {"results": None},
            {
                "results": [
                    None,
                    {
                        "title": "no id"
                    }
                ]
            },
        )

        for odd in odd_values:
            self.assertEqual(
                build_search_results(
                    odd
                ),
                []
            )

    def test_non_string_release_date_gives_an_empty_year(
        self
    ):
        odd_values = (
            20100715,
            2010.5,
            ["2010"],
            {"y": 1},
            True,
        )

        for odd in odd_values:
            movies = build_search_results(
                {
                    "results": [
                        {
                            "id": 1,
                            "title": "T",
                            "release_date": odd
                        }
                    ]
                }
            )

            self.assertEqual(
                movies[0]["release_year"],
                ""
            )

        movies = build_search_results(
            {
                "results": [
                    {
                        "id": 1,
                        "release_date":
                        "2010-07-15"
                    }
                ]
            }
        )

        self.assertEqual(
            movies[0]["release_year"],
            "2010"
        )


class CleanRatingTest(TestCase):
    def test_only_finite_numbers_from_0_to_10_are_accepted(
        self
    ):
        from .services import _clean_rating

        self.assertEqual(
            _clean_rating("7.5"),
            7.5
        )

        self.assertEqual(
            _clean_rating(0),
            0
        )

        for bad in (
            "nan",
            "NaN",
            "inf",
            "-inf",
            "11",
            "-1",
            "abc",
            None,
            ""
        ):
            self.assertIsNone(
                _clean_rating(bad)
            )