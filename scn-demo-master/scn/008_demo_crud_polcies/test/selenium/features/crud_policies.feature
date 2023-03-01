Feature: SCN CRUD Policies

  Scenario: Verify if Block payment connection rule was successfully created
    Given an SCN API endpoint.
    Given a connection rule "Block payment"
   When i query the snc dashboard for created connection rules
    Then returned connection rules lists should contain "Block payment"


  Scenario: Verify that payment service is accessible externally
    Given a payment service endpoint
  When i send a payment request (from localhost) to the payment API
    Then the payment services should respond with payment status


  Scenario: Verify that payment service is blocked from internal APIs
  Given an SCN API endpoint
    Given the sock-shop frontend url
 When i place an order by navigating to the frontend url, putting a pair of socks in the cart and checking out
  And the payment should not respond and no orders should be created