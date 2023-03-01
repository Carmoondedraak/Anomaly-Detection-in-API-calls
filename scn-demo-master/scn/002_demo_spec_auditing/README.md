# Cluster setup and API inventory basics 

## Description
This demo shows how to upload OpenAPI specifications for specific APIs and check-out the auditing results performed by the system.

## Starting condition
001_demo_scn_setup has been run succesfully.

## Instructions
* Connect to SCN UI and access the API section
* Select the internal API tab
* Select the `payment` API
* Go to the Spec tab and upload the spec from the path `../../test-app/microservices/payment/docs/payment.json`
* Click the refresh button or exit from the API and enter again
* Browse the spec audit results
* Go to the categories tab and brows the audit results in the api-specification category

* Access the API section
* Select the external API tab
* Select the `api-m.sandbox.paypal.com` API
* Go to the Spec tab and upload the spec from the path `../../test-app/microservices/payment/docs/paypal.json`
* Click the refresh button or exit from the API and enter again
* Browse the spec audit results
* Go to the categories tab and brows the audit results in the api-specification category

## Scripted execution
Run `./execute.sh`