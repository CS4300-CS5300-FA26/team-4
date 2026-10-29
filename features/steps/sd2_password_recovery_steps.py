from urllib.parse import urlparse

from behave import given, when, then
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse

User = get_user_model()

# --- Password reset send email ---
@when('I click "Forgot Password"')
def step_click_forgot_password(context):
    context.response = context.test.client.get(
        reverse("password_reset")
    )
    assert context.response.status_code == 200

@given('I have an account with the email "{email}"')
def step_account_with_email(context, email):
    context.user = User.objects.create_user(
        username=f"reset_user_{User.objects.count()}",
        email=email,
        password="OldPassword123!"
    )
    context.old_password = "OldPassword123!"

@given("I am on the password reset page")
def step_on_password_reset_page(context):
    context.response = context.test.client.get(
        reverse("password_reset")
    )
    assert context.response.status_code == 200

@when("I submit my registered email address")
def step_submit_registered_email(context):
    context.response = context.test.client.post(
        reverse("password_reset"),
        {"email": context.user.email}
    )

# can test registered or unregistered email
@when('I submit the email "{email}"')
def step_submit_email(context, email):
    context.submitted_email = email
    context.response = context.test.client.post(
        reverse("password_reset"),
        {"email": email}
    )

@then("I should see a message saying a password reset link has been sent")
def step_reset_link_confirmation(context):
    assert context.response.status_code == 302 or (
        context.response.status_code == 200
    )

    # if redirect
    if context.response.status_code == 302:
        context.response = context.test.client.get(
            context.response.url
        )

    # make sure page has password reset link message
    assert context.response.status_code == 200
    assert (
        b"password reset" in context.response.content.lower()
        or b"reset link" in context.response.content.lower()
        or b"email" in context.response.content.lower() # might wanna make this better
    )

@then("a password reset email should be sent to my email address")
def step_email_sent_to_user(context):
    assert len(mail.outbox) > 0 # send at least one email
    assert context.user.email in mail.outbox[-1].to # make sure most recent email went to the user

@then('a password reset email should be sent to "{email}"')
def step_email_sent_to_address(context, email):
    matching_emails = [
        message for message in mail.outbox
        if email in message.to
    ] # check emails that match the user we sent the email to
    assert matching_emails, (
        f"No password reset email was sent to {email}"
    )

# --- Reset password using a valid reset link ---
@given("I have requested a password reset")
def step_request_password_reset(context):
    # test user
    context.user = User.objects.create_user(
        username=f"reset_user_{User.objects.count()}",
        email=f"reset{User.objects.count()}@example.com",
        password="OldPassword123!"
    )
    context.old_password = "OldPassword123!"

    # submit password reset form
    context.response = context.test.client.post(
        reverse("password_reset"),
        {"email": context.user.email}
    )

    matching_emails = [
        message for message in mail.outbox
        if context.user.email in message.to
    ]
    assert matching_emails, "Password reset email was not sent"

    context.reset_email = matching_emails[-1] # save most recent email info

@given("I have opened a valid password reset link")
def step_open_valid_reset_link(context):

    import re # for finding patterns in text

    # look for reset link in email
    links = re.findall(
        r"https?://[^\s<>\"']+|/reset/[^\s<>\"']+",
        context.reset_email.body
    )
    assert links, "No password reset link found in the email"

    link = links[0].rstrip(".,)")
    path = urlparse(link).path
    
    context.response = context.test.client.get(path, follow=True)

    print("Reset link:", link)
    print("Reset path:", path)
    print("Status code:", context.response.status_code)
    print("Response URL:", context.response.get("Location"))
    print("Response content:", context.response.content[:500])

    assert context.response.status_code == 200, (
        f"Expected status 200, got {context.response.status_code}. "
        f"Redirect chain: {context.response.redirect_chain}"
    )
    context.reset_path = context.response.request["PATH_INFO"]

@when("I enter and submit a new valid password")
def step_submit_new_password(context):
    # Django's standard reset URL
    parts = context.reset_path.strip("/").split("/")
    assert len(parts) >= 3, "Unexpected password reset URL"

    # get user ID and token
    uidb64, token = parts[-2], parts[-1]

    # build the password reset page URL
    reset_url = reverse(
        "password_reset_confirm",
        kwargs={"uidb64": uidb64, "token": token}
    )

    context.response = context.test.client.post(
        reset_url,
        {
            "new_password1": "NewPassword456!",
            "new_password2": "NewPassword456!",
        },
        follow=True,
    )

    context.new_password = "NewPassword456!"

@then("my password should be updated successfully")
def step_password_updated(context):
    context.user.refresh_from_db()
    assert context.user.check_password(context.new_password)

@then("I should be able to log in using my new password")
def step_login_with_new_password(context):
    logged_in = context.test.client.login(
        username=context.user.username,
        password=context.new_password
    )
    assert logged_in, "The new password did not work"

@then("I should not be able to log in using my old password")
def step_old_password_rejected(context):
    logged_in = context.test.client.login(
        username=context.user.username,
        password=context.old_password
    )
    assert not logged_in, "The old password still works"