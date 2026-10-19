Feature: Registration and Login (User Story D-1)

  Scenario: User Registration Happy Path
    Given I am on the registration page
    When I submit a valid username, email, and password
    Then a new account is created and I am taken to the home page

  Scenario: User Login Happy Path
    Given I have an existing account
    And I am on the login page
    When I submit my correct credentials
    Then I am logged in and see my personalized home page