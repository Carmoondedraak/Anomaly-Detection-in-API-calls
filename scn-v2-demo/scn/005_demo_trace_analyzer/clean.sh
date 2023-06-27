#!/bin/bash




# load config
source ../config.sh

mkdir -p k8s
PYTHONPATH=${PYTHONPATH} python3 ../tools/execute.py ../config.sh trace-analyzer clean

echo "Waiting for trace analyzer to be ready..."
sleep 20

echo "Trace analyzer service is now ready."


