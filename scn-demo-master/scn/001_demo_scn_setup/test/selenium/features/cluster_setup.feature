Feature: SCN Cluster setup

Scenario: Verify if cluster was successfully created
  Given a Portshift (SNC) API endpoint.
  Given a cluster name
 When i query the snc dashboard for created clusters
    Then response body should not be empty
  And returned cluster list should contain initial cluster name


  Scenario: Verify if cluster APIs were successfully created
  Given a Dashboard (SCN) endpoint url
  Given the sock-shop frontend url
    Given a list of APIs
         | api  |
         | user  |
         | catalogue |
         | orders |
         | payment |
         | carts  |
         | api-m.sandbox.paypal.com      |
 When i place an order by navigating to the frontend url, putting a sock in the cart and checking out.
  And i query the snc dashboard for created APIs
    Then response body should not be empty
  And the returned API list should match those at hand