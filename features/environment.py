import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_test")

import django
django.setup()

from django.core import mail
from django.core.mail import get_connection
from django.test import Client

def before_scenario(context, scenario):
    get_connection()
    mail.outbox.clear()

    # create the Django test client
    context.test = type("TestContext", (), {})()
    context.test.client = Client()