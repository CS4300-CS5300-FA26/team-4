# SD-6: Discovery & Search -- Browse Popular

Feature: Popular Movies and Shows (User Story SD-6)
  As a logged-in user
  I want to browse currently popular movies and shows
  So that I can discover trending content

  Background:
    Given I am logged in

  Scenario: Popular titles are displayed when the home page loads
    Given I am on the Home page
    When the page loads
    Then I should see a Popular section
    And I should see a list of currently popular titles

  Scenario: Popular row displays at least 10 titles with posters
    Given I am on the Home page
    When the page loads
    Then the Popular row should contain at least 10 titles
    And each popular title should have a poster
    And each popular title should have a title displayed

  Scenario: Selecting a popular title opens its details page
    Given I am on the Home page
    When the page loads
    When I select a popular title
    Then I should be taken to that title's details page
    And I should see the selected title's details