# SD-4: Watchlist & History Management -- Watched History and Personal Ratings

Feature: Watched History and Personal Ratings (User Story SD-4)
  As a logged-in user
  I want to mark a title as watched and give it a personal rating
  So that my history and preferences are recorded

# Gherkin Scenarios

  Scenario: Mark a watchlist title as watched
    Given I am logged in
    And a title is in my watchlist
    When I select "Mark as watched"
    Then the title should be marked as watched
    And the title should appear in my viewing history

  Scenario: Mark a title as watched and provide a rating
    Given I am logged in
    And a title is in my watchlist or search results
    When I mark the title as watched
    And I select a personal rating
    And I save my rating
    Then the title should appear in my viewing history
    And my rating should be saved for the title
    And my viewing statistics should be updated

  Scenario: Rate a title in viewing history
    Given I am logged in
    And a title is in my viewing history
    When I select "Rate this"
    And I select a personal rating
    And I save my rating
    Then the title should appear in my viewing history with my rating
    And my saved rating should match the rating I selected