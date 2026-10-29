# SD-5: Discovery & Search -- Search & Filter

Feature: Search and Filter (User Story SD-5)
  As a logged-in user
  I want to search and filter movies and shows by title, genre, year, streaming service, and rating
  So that I can narrow results quickly

  Scenario: Search by title
    Given I am on the search page
    When I enter a movie or show title
    And I submit the search
    Then matching titles should be displayed
    And each result should show its poster and basic information

  Scenario: Filter results by genre
    Given I am on the search page
    And search results are displayed
    When I select a genre filter
    Then only titles matching the selected genre should be displayed

  Scenario: Filter results by release year
    Given I am on the search page
    And search results are displayed
    When I select a release year filter
    Then only titles matching the selected release year should be displayed

  Scenario: Filter results by streaming service
    Given I am on the search page
    And search results are displayed
    When I select a streaming service filter
    Then only titles available on the selected streaming service should be displayed

  Scenario: Filter results by rating
    Given I am on the search page
    And search results are displayed
    When I select a rating filter
    Then only titles matching the selected rating criteria should be displayed

  Scenario: Apply multiple filters
    Given I am on the search page
    And search results are displayed
    When I select a genre filter
    And I select a release year filter
    And I select a streaming service filter
    And I select a rating filter
    Then only titles matching all selected filters should be displayed
    And each result should show its poster and basic information