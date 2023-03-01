# SCN TLS Inspection

## Description
This demo shows how to create  a tls interception rule for an external API and be able to observe intercepted traffic


## Starting condition
* 001_demo_scn_setup has been run succesfully.



## Instructions
* Make sure port forwarding for the sock-shop is running: 
```
kubectl -n sock-shop port-forward deployment/front-end 8079:8079
```
* Connect to the sockshop, browsing at localhost:8079
* Complete a purchase
* Connect to SCN UI and go to Runtime->Connections
* In the visualization options select "Layer 7 attributes"
* Filter by destination workload with the string "pay"
* Show that no layer7 attributes are shown for the interactions with paypal service
* Go to Policies->Connection Policies and create a new Rule as follows:
    * Step 1:
      * Name="inspect paypal"
      * Action="Allow"
      * Intercept https traffic="yes"
    * Step 2:
      * source: By Pod, Any
    * Step 3:
      * By Address, By Domain Name, api-m.sandbox.paypal.com
    * Step 4:
      * Protocol: Http
      * Method: POST
   Make sure to click on "apply policies"
* Connect to the sockshop, browsing at localhost:8079
* Complete a purchase
* Connect to SCN UI and go to Runtime->Connections
* Filter by destination workload with the string "pay"
* Show that layer7 attributes are now shown for the interactions with paypal service

## Scripted execution
Run `./execute.sh`


