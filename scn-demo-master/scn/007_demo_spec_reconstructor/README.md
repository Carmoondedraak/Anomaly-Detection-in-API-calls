# SCN API Traffic Policies

## Description
This demo shows how to reconstruct API specification.


## Starting condition
* 001_demo_scn_setup has been run succesfully.
* 003_demo_token_injection has been run succesfully.


## Instructions
* Make sure port forwarding for the sock-shop is running: 
```
kubectl -n sock-shop port-forward deployment/front-end 8079:8079
```
* Go to APIs->Internal oe External API and select API of choice (for which spec reconstruction should be performed):
    * Click on the "Spec" -> "reconstructed" tabs:
    * Click on "Collect Data"
* Generate some load
    * Using the python load generator
      * Go into the demo-scripts/tools folder and execute "python3 sockshop_client.py"
    * Using the UI:
      * Connect to the sockshop, browsing at localhost:8079
      * Complete a purchase
* Wait for data collection to complete
* Click on the "review"
* Select desired paths to approve and click on "Approve Review" on the top right Button
* The reconstructed spec will be reloaded
## Scripted execution
Run `./execute.sh`

