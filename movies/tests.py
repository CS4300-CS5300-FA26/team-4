from django.test import TestCase
from django.urls import reverse
from .models import Movie

# Create your tests here.

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
