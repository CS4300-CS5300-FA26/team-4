from behave import given, when, then

@given('I am on the Home page')
def visit_home_page(context):
    raise NotImplementedError("Waiting for Home page implementation")

@when('the page loads')
def page_loads(context):
    raise NotImplementedError("Waiting for Popular section implementation")

# --- Popular titles are displayed when the home page loads ---
@then('I should see a Popular section')
def verify_popular_section(context):
    raise NotImplementedError("Waiting for Popular section implementation")

@then('I should see a list of currently popular titles')
def verify_popular_titles(context):
    raise NotImplementedError("Waiting for popular titles implementation")

# --- Popular row displays at least 10 titles with posters ---
@then('the Popular row should contain at least 10 titles')
def verify_popular_count(context):
    raise NotImplementedError("Waiting for Popular row implementation")

@then('each popular title should have a poster')
def verify_popular_posters(context):
    raise NotImplementedError("Waiting for poster implementation")

@then('each popular title should have a title displayed')
def verify_popular_title_names(context):
    raise NotImplementedError("Waiting for title implementation")

# --- Selecting a popular title opens its details page ---
@when('I select a popular title')
def select_popular_title(context):
    raise NotImplementedError("Waiting for popular title selection implementation")

@then("I should be taken to that title's details page")
def verify_popular_detail_page(context):
    raise NotImplementedError("Waiting for movie detail navigation")

@then("I should see the selected title's details")
def verify_selected_title_details(context):
    raise NotImplementedError("Waiting for movie detail implementation")