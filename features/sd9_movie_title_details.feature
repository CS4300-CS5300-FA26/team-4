# SD-9: Title Details

# User Story

Feature: Movie details
  As a logged-in user
  I want to view full details for a movie or show
  So that I can make an informed decision

# Gherkin Scenarios (might need to modify to match github)

  Scenario: View complete movie details
    Given I am logged in
    And a movie has poster, overview, cast, genres, ratings, and streaming information
    When I open the movie details page
    Then I should see the movie poster
    And I should see the movie overview
    And I should see the cast and genres
    And I should see ratings and streaming information

  Scenario: Add a movie from its details page
    Given I am logged in
    And I am viewing a movie details page
    When I add the movie to my watchlist
    Then the movie should appear in my watchlist

  Scenario Outline: Open movie details from different pages
    Given I am logged in
    And a movie is available from "<source>"
    When I select the movie
    Then I should see its details page

    Examples:
      | source          |
      | search          |
      | watchlist       |
      | home            |
      | recommendations |