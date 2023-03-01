#!/bin/bash

export PYTHONPATH=../tools:${PYTHONPATH}

python3 -m behave -f pretty test/features  --no-capture