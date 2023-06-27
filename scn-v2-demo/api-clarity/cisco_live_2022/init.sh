#!/usr/bin/env bash

set -e
set -x

GCP_PROJECT_ID="gcp-etiappsecurity-nprd-62652"
GCP_ZONE="europe-west4-a"
K8S_CLUSTER_NAME="cisco-live-2022"
ISTIO_VERSION="1.13.2"
NATS_OR_APICLARITY="apiclarity"

APICLARITY_DOCKER_REGISTRY="gcr.io/eticloud/scn-demo/cisco_live_2022"
APICLARITY_DOCKER_TAG="cisco-live-2022-devel"
#NAMESPACE_LABEL="istio-injection=enabled"
NAMESPACE_LABEL="SecureApplication-protected=full"

# Processing internal private variables
_K8S_CONTEXT="gke_${GCP_PROJECT_ID}_${GCP_ZONE}_${K8S_CLUSTER_NAME}"
_KONG_NAMESPACE="kong"
_NATS_NAMESPACE="nats"

if [ ${NATS_OR_APICLARITY} = "nats" ]; then
    _TRACE_BACKEND_ADDRESS="nats-proxy.${_NATS_NAMESPACE}"
    _TRACE_BACKEND_PORT="1323"
elif [ ${NATS_OR_APICLARITY} = "apiclarity" ]; then
    _TRACE_BACKEND_ADDRESS="apiclarity-apiclarity.apiclarity"
    _TRACE_BACKEND_PORT="9000"
else
    echo "NATS_OR_APICLARITY must be 'nats' or 'apiclarity'"
    exit 1
fi

_banner() {
    cat <<"EOF"

░█████╗░██████╗░██╗░█████╗░██╗░░░░░░█████╗░██████╗░██╗████████╗██╗░░░██╗
██╔══██╗██╔══██╗██║██╔══██╗██║░░░░░██╔══██╗██╔══██╗██║╚══██╔══╝╚██╗░██╔╝
███████║██████╔╝██║██║░░╚═╝██║░░░░░███████║██████╔╝██║░░░██║░░░░╚████╔╝░
██╔══██║██╔═══╝░██║██║░░██╗██║░░░░░██╔══██║██╔══██╗██║░░░██║░░░░░╚██╔╝░░
██║░░██║██║░░░░░██║╚█████╔╝███████╗██║░░██║██║░░██║██║░░░██║░░░░░░██║░░░
╚═╝░░╚═╝╚═╝░░░░░╚═╝░╚════╝░╚══════╝╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░░╚═╝░░░░░░╚═╝░░░


                 ░█████╗░██╗░██████╗░█████╗░░█████╗░  ██╗░░░░░██╗██╗░░░██╗███████╗  ██████╗░░█████╗░██████╗░██████╗░
                 ██╔══██╗██║██╔════╝██╔══██╗██╔══██╗  ██║░░░░░██║██║░░░██║██╔════╝  ╚════██╗██╔══██╗╚════██╗╚════██╗
                 ██║░░╚═╝██║╚█████╗░██║░░╚═╝██║░░██║  ██║░░░░░██║╚██╗░██╔╝█████╗░░  ░░███╔═╝██║░░██║░░███╔═╝░░███╔═╝
                 ██║░░██╗██║░╚═══██╗██║░░██╗██║░░██║  ██║░░░░░██║░╚████╔╝░██╔══╝░░  ██╔══╝░░██║░░██║██╔══╝░░██╔══╝░░
                 ╚█████╔╝██║██████╔╝╚█████╔╝╚█████╔╝  ███████╗██║░░╚██╔╝░░███████╗  ███████╗╚█████╔╝███████╗███████╗
                 ░╚════╝░╚═╝╚═════╝░░╚════╝░░╚════╝░  ╚══════╝╚═╝░░░╚═╝░░░╚══════╝  ╚══════╝░╚════╝░╚══════╝╚══════╝



                                                                                                 .'\   /`.
                                                                                               .'.-.`-'.-.`.
                                                                                          ..._:   .-. .-.   :_...
                                                                                        .'    '-.(o ) (o ).-'    `.
                                                                                       :  _    _ _`~(_)~`_ _    _  :
                                                                                      :  /:   ' .-=_   _=-. `   ;\  :
                                                                                      :   :|-.._  '     `  _..-|:   :
                                                                                       :   `:| |`:-:-.-:-:'| |:'   :
                                                                                        `.   `.| | | | | | |.'   .'
                                                                                          `.   `-:_| | |_:-'   .'
                                                                                       jgs  `-._   ````    _.-'
                                                                                                ``-------''


EOF
}

_check_binary() {
    local binary=$1
    command -v "$binary" >/dev/null 2>&1 || { echo >&2 "$binary is required but is not installed."; exit 1; }
}

init() {
    git submodule update --init --recursive
}

create_gke_cluster() {
    gcloud --project ${GCP_PROJECT_ID} container clusters create ${K8S_CLUSTER_NAME} --release-channel "regular" --zone ${GCP_ZONE} --num-nodes 3 --enable-ip-alias
    gcloud --project ${GCP_PROJECT_ID} container clusters get-credentials ${K8S_CLUSTER_NAME} --zone ${GCP_ZONE}
}

resize_gke_cluster() {
    gcloud --project ${GCP_PROJECT_ID} container clusters resize ${K8S_CLUSTER_NAME} --zone ${GCP_ZONE} --num-nodes 6
}

create_faster_nodepool() {
    gcloud --project ${GCP_PROJECT_ID} container node-pools create larger-pool --cluster=${K8S_CLUSTER_NAME} --zone ${GCP_ZONE} --machine-type=e2-standard-4 --num-nodes=3
}

delete_gke_cluster() {
    gcloud --project ${GCP_PROJECT_ID} container clusters delete ${K8S_CLUSTER_NAME} --zone ${GCP_ZONE}
}

install_istio() {
    curl -L https://istio.io/downloadIstio | ISTIO_VERSION=${ISTIO_VERSION} TARGET_ARCH=x86_64 sh -
    ./istio-${ISTIO_VERSION}/bin/istioctl install --set profile=minimal -y
}

uninstall_istio() {
    if [ -d "istio-${ISTIO_VERSION}" ]; then
        ./istio-${ISTIO_VERSION}/bin/istioctl x uninstall --purge -y
        kubectl delete namespace istio-system
        rm -rf istio-*
    fi
}

POD_FEED="pod-feed"
create_pod_feed() {
  kubectl run --namespace apiclarity ${POD_FEED} --image=alpine:3.15 --restart=Never -- sleep infinity || true
  kubectl -n apiclarity wait --timeout=1m --for=condition=ready pod ${POD_FEED}
  kubectl cp ../tools apiclarity/${POD_FEED}:/tmp/
  kubectl exec --namespace apiclarity ${POD_FEED} -- apk add curl bash python3 py3-pip
  kubectl exec --namespace apiclarity ${POD_FEED} -- pip3 install requests
}

delete_pod_feed() {
  kubectl delete -n apiclarity pod ${POD_FEED}
}

feed_trace_analyzer() {
  create_pod_feed
  kubectl exec -n apiclarity ${POD_FEED} -- bash -c "UPSTREAM_TELEMETRY_HOST_NAME=${_TRACE_BACKEND_ADDRESS} /tmp/tools/feed.sh ${*}"
}

feed_stats() {
  create_pod_feed
  kubectl exec -n apiclarity ${POD_FEED} -- bash -c "APICLARITY_BASE=http://${_TRACE_BACKEND_ADDRESS} python3 /tmp/tools/generate_traces_stats.py ${*}"
}

push_apiclarity() {
    make -C apiclarity push-docker-backend DOCKER_REGISTRY="${APICLARITY_DOCKER_REGISTRY}" DOCKER_TAG="${APICLARITY_DOCKER_TAG}"
    make -C apiclarity push-docker-plugins DOCKER_REGISTRY="${APICLARITY_DOCKER_REGISTRY}" DOCKER_TAG="${APICLARITY_DOCKER_TAG}"
}

install_apiclarity() {
    sed -e 's/^version: .*$/version: v0.13.0/' -i.bak apiclarity/charts/apiclarity/Chart.yaml

    params=" "
    params="${params} --set apiclarity.env.plugins.STATS_MAX_SAMPLES=100"

    # Do not install the wasm filter as part of the helm chart
    # params="${params} --set trafficSource.envoyWasm.enabled=true"
    # params="${params} --set trafficSource.envoyWasm.namespaces=sock-shop"
    # params="${params} --set trafficSource.envoyWasm.enableIstioVerify=false"
    # params="${params} --debug"

    helm install --create-namespace apiclarity apiclarity/charts/apiclarity -n apiclarity --set global.docker.registry="${APICLARITY_DOCKER_REGISTRY}" --set apiclarity.docker.imageTag="${APICLARITY_DOCKER_TAG}" ${params}
}

uninstall_apiclarity() {
    helm uninstall apiclarity -n apiclarity || true
    kubectl -n apiclarity delete persistentvolumeclaims data-apiclarity-apiclarity-postgresql-0 || true
    kubectl delete namespace apiclarity || true
}

values_apiclarity() {
    helm -n apiclarity get values apiclarity
}

psql_apiclarity() {
    kubectl -n apiclarity exec -it apiclarity-apiclarity-postgresql-0 -- psql apiclarity postgres
}

install_envoy_filter() {
    [ $# -ne 1 ] && echo "You must specify the namespace" && exit 1
    local namespace=$1
    (cd apiclarity/wasm-filters; \
        WASM_FILTER_TRACE_BACKEND_ADDRESS="${_TRACE_BACKEND_ADDRESS}" ./deploy.sh "${namespace}")
}

install_sock_shop() {
    local namespace="sock-shop"
    kubectl create namespace ${namespace} || true
    kubectl label namespace ${namespace} ${NAMESPACE_LABEL} --overwrite
    kubectl -n ${namespace} apply -f ../../test-app/deploy/kubernetes/sock-shop-no-namespace.yaml
    kubectl -n ${namespace} wait --for=condition=ready pod --all
}

uninstall_sock_shop() {
    kubectl delete namespace sock-shop
}

install_mypetstorev2() {
    kubectl apply -f ../../test-apps/mypetstorev2/mypetstorev2-k8sec.yaml
    kubectl -n mypetstorev2 wait --for=condition=ready pod --all
}

uninstall_mypetstorev2() {
    kubectl delete namespace mypetstorev2
}

install_juiceshop() {
    local namespace="juice-shop"
    kubectl create namespace ${namespace} || true
    kubectl label namespace ${namespace} ${NAMESPACE_LABEL} --overwrite
    kubectl --namespace ${namespace} apply -f ../../test-apps/juice-shop/deploy/kubernetes/juice-shop.yaml
    kubectl -n ${namespace} wait --for=condition=ready pod --all
}

uninstall_juiceshop() {
    local namespace="juice-shop"
    kubectl delete namespace ${namespace}
}

install_bookinfo() {
    local namespace="bookinfo"
    kubectl create namespace ${namespace} || true
    kubectl label namespace ${namespace} ${NAMESPACE_LABEL} --overwrite
    kubectl --namespace ${namespace} apply -f https://raw.githubusercontent.com/istio/istio/release-1.14/samples/bookinfo/platform/kube/bookinfo.yaml
    kubectl -n ${namespace} wait --for=condition=ready pod --all
}

uninstall_bookinfo() {
    local namespace="bookinfo"
    kubectl delete namespace ${namespace}
}

install_vapi() {
    helm upgrade --install --create-namespace vapi --namespace vapi vapi/vapi-chart --values=vapi/vapi-chart/values.yaml
    kubectl -n vapi wait --for=condition=ready pod --all
}

uninstall_vapi() {
    helm uninstall vapi --namespace vapi || true
    kubectl delete namespace vapi || true
}

vegeta-setup() {
    kubectl run vegeta --restart=Never --image="peterevans/vegeta" -- /bin/sh -c "apk add curl bash && sleep 99999999"
    kubectl wait --timeout=1m --for=condition=ready pod vegeta
    kubectl cp ../tools vegeta:/tmp/
    #kubectl exec -it vegeta -- /bin/bash
    # echo 'GET http://apiclarity-apiclarity.apiclarity:8080' | vegeta attack -rate=1 -duration=10s > results.bin
    # #     sh -c \
    # "echo 'GET https://www.example.com' | vegeta attack -rate=10 -duration=30s | tee results.bin | vegeta report"
}

vegeta-attack() {
    local qps=$1
    uninstall_apiclarity && install_apiclarity && kubectl -n apiclarity wait --for=condition=ready --timeout=2m pod --all
    sleep 20
    kubectl exec -it vegeta -- /bin/bash -c "cd /tmp/tools/bench && ./init_state.sh && vegeta attack -name=${qps}qps -targets=attack-scenario.vegeta -keepalive -rate=${qps} -duration=5m > results.${qps}qps.bin"
}

play() {
    trap 'trap - SIGTERM && kill -- -$$' SIGINT SIGTERM EXIT

    kubectl --namespace apiclarity port-forward svc/apiclarity-apiclarity 8080    >/dev/null 2>&1 &
    kubectl --namespace apiclarity port-forward svc/apiclarity-apiclarity 9000    >/dev/null 2>&1 &
    kubectl --namespace sock-shop  port-forward svc/front-end             8079:80 >/dev/null 2>&1 &
    kubectl --namespace bookinfo port-forward svc/productpage             9080    >/dev/null 2>&1 &

    echo "======================="
    echo "CTRL-C when you're done"
    echo "======================="
    sleep 2
    wait
}

full_demo() {
    create_gke_cluster
    resize_gke_cluster
    install_istio
    install_apiclarity
    install_sock_shop
    install_envoy_filter sock-shop
    play
}

_check_binary git
_check_binary gcloud
_check_binary kubectl
_check_binary helm

if declare -f "$1" > /dev/null
then

    kubectl config use-context ${_K8S_CONTEXT} || true
    _banner
    "$@"
else
    echo "'$1' is not a known function name" >&2
    echo "Available functions are":
    compgen -A function | grep -v '^_' | sort
    exit 1
fi
