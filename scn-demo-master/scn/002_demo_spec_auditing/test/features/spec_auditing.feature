Feature: API Specification auditing

  Scenario: Verify if service APIs already exist
    Given a portshift (SNC) API endpoint.
    Given 2 APIs, "payment" (internal API) and "api-m.sandbox.paypal.com" (external API).
    When i query the (SNC) API endpoint for "payment" & "api-m.sandbox.paypal.com" APIs.
    Then the returned API list should match those at hand

  Scenario: Verify if api specification was successfully uploaded
    Given a portshift (SNC) API endpoint.
    Given the following API specs with risks.
       | name                       | category | overall  | critical | high | medium | low | unknown |
       | payment                    | internal | CRITICAL |     2    |  2   |   48   |  2  |    6    |
       | api-m.sandbox.paypal.com   | external | CRITICAL |     1    |  0   |   29   |  0  |   41    |
    When  i query the (SNC) API endpoint for the given APIs.
    Then the returned results should not be empty
    And the risks of the returned APIs should match those given


