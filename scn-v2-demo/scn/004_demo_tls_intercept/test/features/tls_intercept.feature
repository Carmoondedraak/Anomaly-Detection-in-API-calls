Feature: SCN TLS Interception

Scenario: Verify if tls-intercept connection rule was successfully created
  Given a portshift (SNC) API endpoint.
  Given a connection rule "Intercept api-m.sandbox.paypal.com"
 When i query the snc dashboard for created connection rules
  Then returned connection rules lists should contain "Intercept api-m.sandbox.paypal.com"