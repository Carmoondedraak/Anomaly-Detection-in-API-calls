#!/bin/bash

# forwarding testkube dashboa
#kubectl port-forward svc/testkube-dashboard -n testkube 8080 >  /dev/null 2>&1 &
#kubectl port-forward svc/testkube-api-server -n testkube 8088 > /dev/null 2>&1 &

# forwarding apiclarity
kubectl port-forward -n apiclarity svc/apiclarity-apiclarity  9999:8080 > /dev/null 2>&1 &