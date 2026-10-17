from behave import when, then

# just a test (won't stay in the final probably)
@when("I open the movie list page")
def step_open_movie_list(context):
    context.response = context.test.client.get("/")

@then("the page should load successfully")
def step_page_loads_successfully(context):
    assert context.response.status_code == 200