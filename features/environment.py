from django.core import mail

def before_scenario(context, scenario):
    mail.outbox.clear()