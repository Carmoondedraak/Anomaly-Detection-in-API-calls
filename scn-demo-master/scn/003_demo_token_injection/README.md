# Token Injection 

## Description
This demo shows how to configure a token and a token injection policy in SCN.

The payment pod of sock-shop is configured to interact with paypal to perform the payment, however at the beginning does not hold a valid token, hence the payment cannot be performed.

By configuring a token and a token injection rule, the payment service acquires a valid token and can perform a successful payment.

## Starting condition
* 001_demo_scn_setup has been run succesfully.
* Obtain a paypal.env file from aduminuc@cisco.com and place it in the tools folder.

## Instructions
* Run the clean.sh script to make sure no token is injected
* Obtain a valid API token for paypal. To do so, run the script `generate_paypal_token.sh` in the tools folder.
* Make sure port forwarding for the sock-shop is running: 
```
kubectl -n sock-shop port-forward deployment/front-end 8079:8079
```
* Connect to the sockshop, browsing at localhost:8079
* Try to complete a purchase and show that it fails
* Run the portforwarding for the vault:
```
kubectl port-forward svc/vault -n securecn-vault 8200
```
* Browse to https://localhost:8200 (Note that Chrome may not work for this, Safari does)
* Authenticate using the vault token that can be obtained as follows:
```
VAULT_SECRET=`kubectl get secret bank-vaults -n securecn-vault -o jsonpath='{.data.vault-root}' | base64 --decode`
```
* Define a secret for paypal at secret/paypal/paypaltoken. Value is the pay pal token as obtained before.
* In SecureCN create a token for the paypal API pointing to the vault secret just created
* In SecureCN create a deployment policy for the payment pod that inject the paypal token at the env variable PAYPAL_ACCESS_TOKEN
* Wait for at least 30 secs for the policies to be effective
* Restart the payment pod: 
```
kubectl -n sock-shop delete pod `kubectl -n sock-shop get pod | grep payment | awk '{print $1}'`
```
* Wait for the pod to be restarted
* In the Sock-shop attempt the payment and show it is succesful

## Scripted execution
Run `./execute.sh`
