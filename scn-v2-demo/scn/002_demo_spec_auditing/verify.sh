#!/bin/bash

# load config
source ../config.sh



export PYTHONPATH=../tools:${PYTHONPATH}

FRONTEND_POD=$(kubectl -n sock-shop get pod | grep front-end | awk '{print $1; exit}')

echo $FRONTEND_POD

disown $(kubectl -n sock-shop port-forward $FRONTEND_POD 8079:8079) &

python3 -m behave -f pretty test/features  --no-capture

FRONTEND_PORT_FORWARD_PROCESS_ID=$(lsof -n -i4TCP:8079 | awk '{print $2}' | awk 'FNR == 2')

echo $FRONTEND_PORT_FORWARD_PROCESS_ID

kill -9 $FRONTEND_PORT_FORWARD_PROCESS_ID