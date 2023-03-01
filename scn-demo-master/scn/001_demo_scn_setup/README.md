# Cluster setup and API inventory basics 

## Description
This demo shows how to create a new cluster in SCN, connect it to a customer k8s cluster where a test application runs.

Once the cluster is connected the user is able to see:
* All pods part of the test application.
* All connections between pods and between pods and external services.
* Internal APIs identified and scored based on workload risk.
* External APIs identified and scored based on external telemetry.


## Starting condition
* A running k8s cluster where demo app will be instantiated.
* A running SCN instance where demo will be running. 

## Instructions
* Make sure the k8sec context points to the cluster to be used for the test application
* Connect to SCN UI and create a new cluster. Make sure to enable Token Injection.
* Follow the instructions to install the SCN bundle in the cluster
* Deploy the test application
```
kubectl -n sock-shop apply -f ../test-app/deploy/kubernetes/complete-demo.yaml --validate=false
```
* Run the port forwarding
```
kubectl -n sock-shop port-forward deployment/front-end 8079:8079
```
* Connect to the sock-shop, register a user and complete an order
* Connect to SCN and show:
    * Dashboard
    * Navigator
    * Internal API 
    * External API

## Scripted execution
Run `./execute.sh`
