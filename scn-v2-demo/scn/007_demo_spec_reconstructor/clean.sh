#!/bin/bash

source ../config.sh

PYTHONPATH=${PYTHONPATH} python3 ../tools/execute.py ../config.sh spec-reconstructor clean

