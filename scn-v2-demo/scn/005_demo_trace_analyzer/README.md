# Trace Analyzer 

## Description
This demo shows how to generate and view traces in SCN.

The Trace Analyzer is configured to capture and display information about mal practices (such as using password in header, using weak JWT token in header etc.) performed by users/services in the sock-shop microservice stack.

## Recording
https://cisco-my.sharepoint.com/:v:/p/aduminuc

## Starting condition
* 001_demo_scn_setup has been run succesfully.
* 002_demo_spec_auditing has been run succesfully.
* 003_demo_token_injection has been run succesfully.
* 004_demo_tls_intercept has been run succesfully.

## Instructions
* Run the clean.sh script to make sure no token is injected
* Configure config.sh with a valid PAYPAL_ACCESS_TOKEN. To obtain one, run the script `generate_paypal_token.sh` in the tools folder.
* Make sure port forwarding for the sock-shop is running: 
```
kubectl -n sock-shop port-forward `kubectl -n sock-shop get pod | grep front-end | awk '{print $1}'` 8079:8079
```
* Connect to the sockshop, browsing at localhost:8079
* Complete a purchase
* Connect to SCN UI and go to :
   * APIs->INTERNAL APIs->orders->Categories->Application and/or Authentication
   * APIs->INTERNAL APIs->payment->Categories->Application and/or Authentication
   * APIs->EXTERNAL APIs->api-m.sandbox.paypal.com->Categories->Application and/or Authentication

## Scripted execution
Run `./execute.sh`
