#!/bin/bash

source config.sh

if [[ ${USE_VENV} == "True" ]]; then
  source ${BASE_DIR}/env/bin/activate
  if [[ $? != 0 ]]
  then
      echo "Creating virtual environment"
      python3 -m venv env
      source env/bin/activate
  fi
fi

pip3 install -r requirements.txt
