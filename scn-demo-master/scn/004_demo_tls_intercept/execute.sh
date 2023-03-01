#!/bin/bash




# load config
source ../config.sh 


./clean.sh
PYTHONPATH=${PYTHONPATH} python3 ../tools/execute.py ../config.sh tls-intercept