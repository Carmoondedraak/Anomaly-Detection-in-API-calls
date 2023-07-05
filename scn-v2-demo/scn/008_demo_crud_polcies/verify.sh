#!/bin/bash


source ../config.sh


export PYTHONPATH=../tools:${PYTHONPATH}

PAYMENT_POD=$(kubectl -n sock-shop get pod | grep payment | awk '{print $1; exit}')

echo $PAYMENT_POD

disown $(kubectl -n sock-shop port-forward $PAYMENT_POD 8002:80) &

FRONTEND_POD=$(kubectl -n sock-shop get pod | grep front-end | awk '{print $1; exit}')

echo $FRONTEND_POD

disown $(kubectl -n sock-shop port-forward $FRONTEND_POD 8079:8079) &

if [ "$1" = "selenium" ]
then
  python3 -m behave -f pretty test/selenium/features --no-capture
fi

python3 -m behave -f pretty test/sock-shop/features --no-capture

PAYMENT_PORT_FORWARD_PROCESS_ID=$(lsof -n -i4TCP:8002 | awk '{print $2}' | awk 'FNR == 2')

echo $PAYMENT_PORT_FORWARD_PROCESS_ID

kill -9 $PAYMENT_PORT_FORWARD_PROCESS_ID

FRONTEND_PORT_FORWARD_PROCESS_ID=$(lsof -n -i4TCP:8079 | awk '{print $2}' | awk 'FNR == 2')

echo $FRONTEND_PORT_FORWARD_PROCESS_ID

kill -9 $FRONTEND_PORT_FORWARD_PROCESS_ID