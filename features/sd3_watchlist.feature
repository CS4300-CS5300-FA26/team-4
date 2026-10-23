# SD-3: Watchlist & History Management -- Add Watchlist

Feature: Personal watchlist (User Story SD-3)
  As a logged-in user
  I want to add titles to my watchlist
  So that I can track what I want to watch

# Gherkin Scenarios

  Scenario: Add a title to my watchlist
    Given I am logged in
    And a movie exists that is not in my watchlist
    When I add the movie to my watchlist
    Then the movie should appear in my watchlist
    And the movie should be saved to my account

  Scenario: Prevent duplicate watchlist entries
    Given I am logged in
    And a movie is already in my watchlist
    When I add the same movie again
    Then the movie should appear only once in my watchlist
    And I should see a message that the movie is already on my list