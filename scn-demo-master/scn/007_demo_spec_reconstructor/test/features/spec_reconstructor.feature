Feature: Spec Reconstructor

Scenario: Verify if API reconstruction was successful on a given API
  Given a Portshift (SNC) API endpoint.
  Given a "user" API.
 When spec reconstruction is performed on the user API.
  Then the status of the reconstruction process should be "DONE".
  Then the reconstructed spec (file) should not be empty.