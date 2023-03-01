# SCN API Traffic Policies

## Description
This demo shows how to create connection policies and block specific calls towards specific APIs.


## Starting condition
* 001_demo_scn_setup has been run succesfully.
* 003_demo_token_injection has been run succesfully.
* 004_demo_tls_intercept has been run succesfully.


## Instructions
* Make sure port forwarding for the sock-shop is running: 
```
kubectl -n sock-shop port-forward deployment/front-end 8079:8079
```
* Connect to the sockshop, browsing at localhost:8079
* Complete a purchase
* Show it is successful
* Go to Policies->Connection Policies and crate a new Rule as follows:
    * Step 1:
      * Name="block payments"
      * Action="Block"
      * Intercept https traffic="no"
    * Step 2:
      * source: By Pod, Any
    * Step 3:
      * destination: By Pod, payment
    * Step 4:
      * Protocol: Http
      * Method: POST
   Make sure to click on "apply policies"
* Connect to the sockshop, browsing at localhost:8079
* Complete a purchase and show it is failing
* Connect to SCN UI and go to Runtime->Connections
* Filter by destination workload with the string "pay"
* Show that the POST to the payment pod has been blocked.

## Scripted execution
Run `./execute.sh`

