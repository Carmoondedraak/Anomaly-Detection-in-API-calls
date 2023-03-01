Feature: Token Injection

  Scenario: Verify if payment can be made successfully after a valid token is injected into the payment pod
  Given a portshift (SNC) API endpoint
    Given the sock-shop frontend url
    Given a list of APIs
         | api  |
         | payment |
         | api-m.sandbox.paypal.com      |
 When i place an order by navigating to the frontend url, putting a sock in the cart and checking out
  And i query the portshift (SNC) API endpoint for available APIs
  Then the payment and paypal apis should be in the result list