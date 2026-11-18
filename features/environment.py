import os

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings_test"

import django
django.setup()

from django.core import mail
from django.core.mail import get_connection
from django.test import Client, SimpleTestCase
from movies.models import Movie

def before_scenario(context, scenario):
    get_connection()
    mail.outbox.clear()

    # create the Django test client
    context.test = SimpleTestCase()
    context.test.client = Client()

def after_scenario(context, scenario):
    sd7_ids = getattr(context, 'sd7_created_movie_ids', [])
    sd10_ids = getattr(context, 'sd10_created_movie_ids', [])

    movie_ids = sd7_ids + sd10_ids

    if movie_ids:
        Movie.objects.filter(pk__in=movie_ids).delete()