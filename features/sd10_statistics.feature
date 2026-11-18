
# SD-10: Statistics

Feature: Viewing Statistics (User Story SD-10)
  As a logged-in user
  I want to view simple viewing statistics like total watched and genres
  So that I can see my watching patterns

  Background:
    Given I am logged in

  Scenario: View total watched titles and genre statistics
    Given I have marked several titles as watched
    When I open the Statistics page
    Then I should see my total number of watched titles
    And I should see statistics about the genres I watch most
    And my genre statistics should be returned as structured data

  Scenario: View the statistics dashboard on the Watchlist page
    When I open my Watchlist page
    Then I should see the statistics dashboard
    And I should see the watched genre chart
    And the dashboard styles and script should be included