# SD-1: Account Management – Register and Login

Feature: Registration and Login (User Story SD-1)
  As a new user
  I want to register and log in
  So that I can securely use the application

# Gherkin Scenarios

  Scenario: User Registration Happy Path
    Given I am on the registration page
    When I submit a valid username, email, and password
    Then a new account is created and I am taken to the home page

  Scenario: User Login Happy Path
    Given I have an existing account
    And I am on the login page
    When I submit my correct credentials
    Then I am logged in and see my personalized home page

  Scenario: Prevent duplicate account registration
    Given an account already exists with my email
    When I register using the same email
    Then I should see a duplicate email error
    And the duplicate account should not be created

  Scenario: Reject invalid login credentials
    Given I have an existing account
    When I log in with an incorrect password
    Then I should see an invalid login error
    And I should not be logged in