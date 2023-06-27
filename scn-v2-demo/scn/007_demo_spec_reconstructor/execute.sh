#!/bin/bash

# load config
source ../config.sh

./clean.sh

FRONTEND_POD=$(kubectl -n sock-shop get pod | grep front-end | awk '{print $1; exit}')

echo $FRONTEND_POD

disown $(kubectl -n sock-shop port-forward $FRONTEND_POD 8079:8079) &

PYTHONPATH=${PYTHONPATH} python3 ../tools/execute.py ../config.sh spec-reconstructor

FRONTEND_PORT_FORWARD_PROCESS_ID=$(lsof -n -i4TCP:8079 | awk '{print $2}' | awk 'FNR == 2')

echo $FRONTEND_PORT_FORWARD_PROCESS_ID

kill -9 $FRONTEND_PORT_FORWARD_PROCESS_ID

