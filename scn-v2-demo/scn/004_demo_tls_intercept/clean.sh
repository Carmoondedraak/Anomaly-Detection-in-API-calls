#!/bin/bash




# load config
source ../config.sh 



PYTHONPATH=${PYTHONPATH} python3 ../tools/execute.py ../config.sh tls-intercept clean



