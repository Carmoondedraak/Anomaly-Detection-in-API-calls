Feature: Trace Analysis

  Scenario: Verify if expected traces were generated
  Given an SNC API endpoint
    Given the sock-shop frontend url
    Given the following "application" traces:
       | api                       | api-type     | overall   | critical | high | medium | low | unknown |
       | orders                     | internal     |   High    |     0    |  2   |    0   |  0  |     0   |
       | payment                    | internal     |   High    |     0    |  1   |    0   |  0  |     0   |
       | api-m.sandbox.paypal.com   | external     |   High    |     0    |  1   |    0   |  0  |     0   |
    Given the following traces for "authentication":
       | api                       | api-type     | overall   | critical | high | medium | low | unknown |
       | orders                     | internal     |   High    |     0    |  0   |    0   |  0  |     0   |
       | payment                    | internal     |   High    |     0    |  3   |    1   |  0  |     0   |
       | api-m.sandbox.paypal.com   | external     |   High    |     0    |  0   |    0   |  0  |     0   |
  When i place an order by navigating to the frontend url, putting a pair socks in the cart and checking out
  And i query the portshift (SNC) API endpoint for available traces
    Then the returned traces should match those given