#!/bin/bash


source ../config.sh
source ../env/bin/activate

export PYTHONPATH=../tools:${PYTHONPATH}

behave -f pretty test/features  --no-capture