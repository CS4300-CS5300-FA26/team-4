# SD-2: Account Management -- Password Recovery

Feature: Password Recovery (User Story SD-2)
  As a registered user
  I want to recover my account if I forget my password
  So that I do not lose access to my data

# Gherkin Scenarios

Scenario: Request a password reset with a registered email
    Given I have an account with the email "registered@example.com"
    And I am on the login page
    When I click "Forgot Password"
    And I submit my registered email address
    Then I should see a message saying a password reset link has been sent
    And a password reset email should be sent to my email address

  Scenario: Submit an email on the password reset page
    Given I have an account with the email "person@example.com"
    And I am on the password reset page
    When I submit the email "person@example.com"
    Then I should see a message saying a password reset link has been sent
    And a password reset email should be sent to "person@example.com"

  Scenario: Reset password using a valid reset link
    Given I have requested a password reset
    And I have opened a valid password reset link
    When I enter and submit a new valid password
    Then my password should be updated successfully
    And I should be able to log in using my new password
    And I should not be able to log in using my old password