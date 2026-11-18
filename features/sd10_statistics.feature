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
    And my genre statistics should be returned as structured data    # placeholder until frontend is implemented

    # And I should see a visual representation of my genre statistics