# SD-1: Account Management – Register and Login

# User Story

Feature: Account registration and login
  As a new user
  I want to register and log in
  So that I can securely use the application

# Gherkin Scenarios (might need to modify to match github)

  Scenario: Register a new account
    Given I am on the registration page
    When I register with a valid email and password
    Then my account should be created
    And I should be logged in

  Scenario: Prevent duplicate account registration
    Given an account already exists with my email
    When I register using the same email
    Then I should see an error message
    And the duplicate account should not be created

  Scenario: Log in with valid credentials
    Given I have an existing account
    When I log in with the correct email and password
    Then I should be logged in
    And I should have access to my personal watchlist

  Scenario: Reject invalid login credentials
    Given I have an existing account
    When I log in with an incorrect password
    Then I should see an error message
    And I should not be logged in