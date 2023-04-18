#!/bin/bash


# Prerequisite:
#   A running k8s cluster where test app can be instantiated.
#   A running SCN instance where demo will be running

# load config
source ../config.sh


function usage() {
    cat <<EOF
usage: $PROGNAME [-h|--help] [-u|--uninstall] 
    -h:                 Print this helps and exits
    -u | --uninstall:   Uninstall bundle
EOF
}

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
        -u|--uninstall)
            uninstall="True"; shift ;
            ;;
        -y|--yes)
            forceyes="True"; shift ;
            ;;
        *)
            break;
	esac
done

echo "About to run the script against context ${K8S_CONTEXT} and scn instance at ${SCN_HOST}"
if [[ ${forceyes} != "True" ]]; then
    read -p "Continue [y/N]?" yn
    if [[ ${yn} != "y" ]]; then
        echo "Bye!"
        exit 0
    fi
fi


../002_demo_spec_auditing/clean.sh
../003_demo_token_injection/clean.sh --no-restart
../004_demo_tls_intercept/clean.sh

kubectl config use-context ${K8S_CONTEXT}

if [[ ${uninstall} == "True" ]]; then
  __bundle/install_bundle.sh --uninstall --force-remove-vault
  kubectl delete clusterrolebindings.rbac.authorization.k8s.io portshift-agent
  PYTHONPATH=${PYTHONPATH} python3 ../tools/execute.py ../config.sh setup clean
fi

if [[ ${WITH_KONG} == "True" ]]; then
kubectl delete namespace kong
fi

if [[ ${WITH_TYK} == "True" ]]; then
kubectl delete namespace tyk
fi

kubectl delete namespace ${APP_NAMESPACE}
kubectl delete namespace istio-system
kubectl delete namespace securecn-vault

rm -rf tracing_certs vault_certs __bundle

