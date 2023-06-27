#!/bin/bash

# Usage:
#   check-status.sh docker
#   check-status.sh k8s
#   check-status.sh istio

function check_status_docker() {
  OUTPUT=$(docker info 2>&1)
  EXIT_CODE=$?
  if [ $EXIT_CODE -ne 0 ]; then
    printf "\n[%s] Docker is not ready yet.\n" "$(date)"
    cat /var/log/dockerd-entrypoint.log
    return 1
  else
    printf "\n[%s] Docker is ready to go.\n" "$(date)"
#    echo "${OUTPUT}"
    return 0
  fi
}

function check_status_k8s() {
  OUTPUT=$(kubectl cluster-info 2>&1)
  EXIT_CODE=$?
  if [ $EXIT_CODE -ne 0 ]; then
    printf "\n[%s] K8s cluster is not ready yet.\n" "$(date)"
    cat /var/log/kind.log
    return 1
  else
    printf "\n[%s] K8s cluster is ready to go.\n" "$(date)"
#    echo "${OUTPUT}"
    return 0
  fi
}

function check_status_istio() {
  # https://istio.io/latest/docs/setup/install/istioctl/#verify-a-successful-installation
  istioctl manifest generate --set profile=${ISTIO_PROFILE} > /tmp/istio-generated-manifest.yaml
  OUTPUT=$(istioctl verify-install -f /tmp/istio-generated-manifest.yaml 2>&1)
  EXIT_CODE=$?
  if [ $EXIT_CODE -ne 0 ]; then
    printf "\n[%s] Istio is not ready yet.\n" "$(date)"
    cat /var/log/istio.log
    return 1
  else
    printf "\n[%s] Istio is ready to go.\n" "$(date)"
#    echo "${OUTPUT}"
    return 0
  fi
}

function check_status() {
  # Repeatedly (every RETRY_WAIT_TIME) check status until success or until timeout (RETRY_MAX_TIME).
  RETRY_MAX_TIME=90
  RETRY_WAIT_TIME=5
  until [ "${RETRY_WAIT_TIME}" -eq ${RETRY_MAX_TIME} ] || $1; do
    sleep $(( RETRY_WAIT_TIME++ ))
  done
  [ "${RETRY_WAIT_TIME}" -lt 1 ]
}

echo "[$(date)] Checking status for ${1}..."
if [[ "$1" == "docker" ]]; then
  check_status check_status_docker
elif [[ "$1" == "k8s" ]]; then
  check_status check_status_k8s
elif [[ "$1" == "istio" ]]; then
  check_status check_status_istio
else
  echo "Invalid arg '${1}'. Valid args: docker, k8s, istio."
  exit 1
fi
