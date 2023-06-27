Feature: Fuzzing/Testing

  Scenario: Verify if expected findings were generated
  Given an SNC API endpoint
    Given the sock-shop frontend url
    Given the following "application" findings:
       | api                       | api-type     | overall   | critical | high | medium | low | unknown |
       | payment                   | internal     |   High    |     0    |  3   |    1   |  0  |     0   |
  When i query the portshift (SNC) API endpoint for available findings
    Then the returned findings should match those given