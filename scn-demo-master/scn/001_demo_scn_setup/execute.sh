#!/bin/bash


# Prerequisite:
#   A running k8s cluster where test app can be instantiated.
#   A running SCN instance where demo will be running

# load config
source ../config.sh

echo "About to run the script against context ${K8S_CONTEXT} and scn instance at ${SCN_HOST}"
read -p "Continue [y/N]?" yn
if [[ ${yn} != "y" ]]; then
    echo "Bye!"
    exit 0
fi

function usage() {
    cat <<EOF
usage: $PROGNAME [-h|--help] [-u|--uninstall]
    -h:                 Print this helps and exits
    -s | --soft:   Don't reinstall bundle
EOF
}

uninstall="--uninstall"
# Process args and set variables
shopt -s nocasematch
PROGNAME=$(basename "$0")
while [[ $# -ge 1 ]]; do
	opt="$1"
	case $opt in
        -h|--help)
            usage;
            exit 0; shift;
            ;;
        -s|--soft)
            uninstall=""; shift ;
            ;;
        *)
            break;
	esac
done

./clean.sh --yes ${uninstall}

kubectl config use-context ${K8S_CONTEXT}

mkdir __bundle

PYTHONPATH=${PYTHONPATH} python3 ../tools/execute.py ../config.sh setup
# read -p "Replace the bundle if you want and then press return"

tar xzvf __bundle/bundle.tgz -C __bundle

if [[ ${uninstall} == "--uninstall" ]]; then
    __bundle/install_bundle.sh
fi
kubectl apply -f ${APP_PATH_MANIFEST} --validate=false
  
echo "To access the test app locally type the following in a different window:"
echo "kubectl -n sock-shop port-forward deployment/front-end 8079:8079"
echo " and then browse to http://localhost:8079"

POD_STATUS=""
WANTED_STATUS="1/1"
if [[ ${WITH_ENVOY} == "True" ]]; then
  WANTED_STATUS="3/3"
fi

while [ "$POD_STATUS" != "$WANTED_STATUS" ]
do
    echo "Waiting for services to be ready ..."
    POD_STATUS=$(kubectl -n sock-shop get pod | grep orders | awk '{print $2; exit}')
    sleep 1
done
echo "User service is now ready."


if [[ ${WITH_KONG} == "True" ]]; then
  echo "Installing kong"
  kubectl apply -f "${KONG_PATH}/deployment.yaml"

  echo "Create ingress in ${APP_NAMESPACE}"
  kubectl apply -f "${KONG_PATH}/ingress.yaml"

  PROXY_IP=""
  while [ -z "$PROXY_IP" ];
  do
    PROXY_IP=$(kubectl get -o jsonpath="{.status.loadBalancer.ingress[0].ip}" service -n kong kong-proxy)
    echo "Waiting for Load Balancer to be setup"
    sleep 1
  done

  echo "KONG_IP_ADDRESS: ${PROXY_IP}"
fi

if [[ ${WITH_TYK} == "True" ]]; then
  echo "Installing tyk"
  cd ${TYK_PATH}
  ./launch-tyk.sh
  cd -
  PROXY_IP=""
  while [ -z "$PROXY_IP" ];
  do
    PROXY_IP=$(kubectl get -o jsonpath="{.status.loadBalancer.ingress[0].ip}" service -n tyk tyk-svc)
    echo "Waiting for Load Balancer to be setup"
    sleep 1
  done

  echo "TYK IP Address: ${PROXY_IP}"
fi

