#!/bin/bash

# Deploy Tyk & Redis
kubectl create namespace tyk --dry-run=1 -o yaml | kubectl apply -f -
kubectl apply -f . -n tyk