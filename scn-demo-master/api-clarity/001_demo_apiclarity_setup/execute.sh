#!/usr/bin/env bash

source ../config.sh

banner() {
  cat <<"EOF"

 ███▄ ▄███▓ █     █░ ▄████▄     ▓█████▄ ▓█████  ███▄ ▄███▓ ▒█████
▓██▒▀█▀ ██▒▓█░ █ ░█░▒██▀ ▀█     ▒██▀ ██▌▓█   ▀ ▓██▒▀█▀ ██▒▒██▒  ██▒
▓██    ▓██░▒█░ █ ░█ ▒▓█    ▄    ░██   █▌▒███   ▓██    ▓██░▒██░  ██▒
▒██    ▒██ ░█░ █ ░█ ▒▓▓▄ ▄██▒   ░▓█▄   ▌▒▓█  ▄ ▒██    ▒██ ▒██   ██░
▒██▒   ░██▒░░██▒██▓ ▒ ▓███▀ ░   ░▒████▓ ░▒████▒▒██▒   ░██▒░ ████▓▒░
░ ▒░   ░  ░░ ▓░▒ ▒  ░ ░▒ ▒  ░    ▒▒▓  ▒ ░░ ▒░ ░░ ▒░   ░  ░░ ▒░▒░▒░
░  ░      ░  ▒ ░ ░    ░  ▒       ░ ▒  ▒  ░ ░  ░░  ░      ░  ░ ▒ ▒░
░      ░     ░   ░  ░            ░ ░  ░    ░   ░      ░   ░ ░ ░ ▒
       ░       ░    ░ ░            ░       ░  ░       ░       ░ ░
                    ░            ░


                                                         Cisco 2022

EOF
}

instructions() {
  cat <<EOF
                       ╦┌┐┌┌─┐┌┬┐┬─┐┬ ┬┌─┐┌┬┐┬┌─┐┌┐┌┌─┐
─────────────────────  ║│││└─┐ │ ├┬┘│ ││   │ ││ ││││└─┐  ─────────────────────
                       ╩┘└┘└─┘ ┴ ┴└─└─┘└─┘ ┴ ┴└─┘┘└┘└─┘

$1

───────────────────────────────────────────────────────────────────────────────
EOF
}

install_istio() {
  echo "Installing API istio"

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

install_sock_shop() {
  echo "Installing sock-shop stack"
  kubectl -n ${APP_NAMESPACE} apply -f ${APP_PATH_MANIFEST} --validate=false

  kubectl label namespace "${APP_NAMESPACE}" istio-injection=enabled --overwrite
}

uninstall_sock_shop() {
  kubectl delete ns ${APP_NAMESPACE}
}

install_envoy_filter() {
  echo "Installing envoy wasm filter to namespace ${APP_NAMESPACE}"
  (cd ${APICLARITY_FOLDER}/wasm-filters; \
   WASM_FILTER_TRACE_BACKEND_ADDRESS=${WASM_FILTER_TRACE_BACKEND_ADDRESS} ./deploy.sh ${APP_NAMESPACE})
}

build_apiclarity() {
  if [[ "${no_build}" != "TRUE" ]]; then
    make -C ${APICLARITY_FOLDER} push-docker-backend DOCKER_REGISTRY=${API_CLARITY_IMAGE_REGISTRY}
    make -C ${APICLARITY_FOLDER} push-docker-plugins DOCKER_REGISTRY=${API_CLARITY_IMAGE_REGISTRY}
  fi
}

install_apiclarity() {
  COMMIT_HASH=$(cd ${APICLARITY_FOLDER}; git rev-parse HEAD)
  helm install --values ./values.yaml --set apiclarity.docker.imageTag=${COMMIT_HASH} --set global.docker.registry=${API_CLARITY_IMAGE_REGISTRY} --create-namespace apiclarity ./${APICLARITY_FOLDER}/charts/apiclarity -n apiclarity

  # Upload assets to the persistent volume of apiclarity
  local pod=$(kubectl -n apiclarity get pods --selector='app=apiclarity-apiclarity' --output='jsonpath={.items[0].metadata.name}')
  kubectl -n apiclarity wait --timeout=5m --for=condition=ready pod -l 'app=apiclarity-apiclarity'
  kubectl cp -c apiclarity ../tools/assets apiclarity/${pod}:/apiclarity/

  # Restart API Clarity to read the assets
  kubectl -n apiclarity rollout restart deployment apiclarity-apiclarity

  # Wait for it to be ready
  kubectl -n apiclarity wait --for=condition=ready pod -l app=apiclarity-apiclarity
}

uninstall_api_clarity() {
  helm uninstall apiclarity -n apiclarity || true
  kubectl -n apiclarity delete persistentvolumeclaims data-apiclarity-apiclarity-postgresql-0 || true
  if [[ ! "$1" == "--keep-namespace" ]];then
     kubectl delete ns apiclarity
  fi
}

install_kong_and_api_clarity_plugin() {
  echo "Installing kong"
  kubectl apply -f ../../common/kong/deployment.yaml

  echo "Create ingress in ${APP_NAMESPACE}"
  kubectl apply -f ../../common/kong/ingress.yaml

  echo "Installing api-clarity kong plugin"
  ${APICLARITY_FOLDER}/plugins/gateway/kong/deploy/deploy.sh

  PROXY_IP=""
  while [ -z "$PROXY_IP" ];
  do
    PROXY_IP=$(kubectl get -o jsonpath="{.status.loadBalancer.ingress[0].ip}" service -n kong kong-proxy)
    echo "Waiting for Load Balancer to be setup"
    sleep 1
  done

  global_kong_ip=${PROXY_IP}
  echo "${PROXY_IP}"
}

protect_kong() {
  local user="aduminuc"
  local key="verysecret"

  kubectl -n kong create secret generic ${user}-apikey  \
    --from-literal=kongCredType=key-auth  \
    --from-literal=key=${key}

# apiVersion: configuration.konghq.com/v1
# kind: KongConsumer
# metadata:
#   name: ${user}
#   annotations:
#     kubernetes.io/ingress.class: kong
# username: ${user}
# ---
  cat <<EOF | kubectl -n kong apply -f -
apiVersion: configuration.konghq.com/v1
kind: KongConsumer
metadata:
  name: ${user}
  annotations:
    kubernetes.io/ingress.class: kong
username: ${user}
credentials:
- ${user}-apikey
---
apiVersion: configuration.konghq.com/v1
kind: KongClusterPlugin
metadata:
  name: httpbin-auth
  annotations:
    kubernetes.io/ingress.class: kong
  labels:
    global: "true"
plugin: key-auth
EOF
}

uninstall_kong() {
  kubectl delete -f ../../common/kong/deployment.yaml
  kubectl delete -f ../../common/kong/ingress.yaml
  kong delete namespace kong
}

POD_FEED="pod-feed"
create_pod_feed() {
  kubectl run -n apiclarity ${POD_FEED} --image=alpine:3.15 --restart=Never -- sleep infinity || true
  kubectl -n apiclarity wait --timeout=1m --for=condition=ready pod ${POD_FEED}
  kubectl cp ../tools apiclarity/${POD_FEED}:/tmp/
  kubectl exec -n apiclarity ${POD_FEED} -- apk add curl bash python3 py3-pip
  kubectl exec -n apiclarity ${POD_FEED} -- pip3 install requests
}

delete_pod_feed() {
  kubectl delete -n apiclarity pod ${POD_FEED}
}

feed_trace_analyzer() {
  create_pod_feed
  kubectl exec -n apiclarity ${POD_FEED} -- bash -c "UPSTREAM_TELEMETRY_HOST_NAME=apiclarity-apiclarity.apiclarity /tmp/tools/feed.sh ${*}"
}

feed_stats() {
  create_pod_feed
  kubectl exec -n apiclarity ${POD_FEED} -- bash -c "APICLARITY_BASE=http://apiclarity-apiclarity.apiclarity python3 /tmp/tools/generate_traces_stats.py ${*}"
}

reserve_static_ip() {
  local rc_static_ip="${whoami}-apiclarity-demo-ip"
  gcloud compute addresses create ${rc_static_ip} --project ${GCP_PROJECT} --region ${GCP_REGION} || true
  ip=$(gcloud compute addresses describe ${rc_static_ip} --project ${GCP_PROJECT} --region ${GCP_REGION} --format='value(address)')
  echo "${ip}"
}

create_lb() {
  [[ $# -ne 1 ]] && (echo "Missing LB ip address"; exit 1)
  local ip=$1

  cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: lb-apiclarity
  namespace: apiclarity
spec:
  selector:
    app: apiclarity-apiclarity
  ports:
  - port: 9999
    targetPort: 8080
  type: LoadBalancer
  loadBalancerIP: "${ip}"
---
apiVersion: v1
kind: Service
metadata:
  name: lb-sock-shop
  namespace: sock-shop
spec:
  selector:
    name: front-end
  ports:
  - port: 8079
    targetPort: 8079
  type: LoadBalancer
  loadBalancerIP: "${ip}"
EOF
}

uninstall() {
  read -p "Are you sure to purge Istio and APIClarity [y/N]?" yn
  if [[ ${yn} != "y" ]]; then
    exit 0
  fi
  echo "[+] Uninstalling APIClarity"
  uninstall_api_clarity &
  echo "[+] Uninstalling istio..."
  uninstall_istio &
  echo "[+] Uninstalling sock-shop"
  uninstall_sock_shop &
  echo "[+] Uninstalling kong"
  uninstall_kong &

  wait
}

usage() {
    cat <<EOF
usage: $PROGNAME [-h|--help] [-u|--uninstall]

    For MWC:
                ./execute.sh --public-expose --kong --no-build # This installs everything
                                                               # This is safe to run this command mulitple time, it won't delete anything
                ./execute.sh respin-apiclarity # Uninstall/Install APIClarity, deleting all data
                ./execute.sh uninstall # Uninstall everything


    respin-apiclarity      Full respin of APIClarity (uninstall, reinstall), then exit
    repush-apiclarity      Full build, push and respin
    uninstall              !!! WARNING !!! Purge everything before installing, then exit

    feed-trace-analyzer    Feed traces (./execute.sh feed-trace-analyzer 1), then exit
    feed-stats             Feed stats (./execute.sh feed-stats 1 /tmp/tools/provided_spec.json), then exit
    delete-pod-feed        Delete the pod feed, then exit

    --kong                 Install and configure kong gateway as well
    --public-expose        publicly expose the sock-shop and apiclarity, then exit

    --force-repo-deletion  Delete APIClarity Repo
    --no-build             Do not build/push APIClarity image
    -h:                    Print this helps and exits
EOF
}

#if [ "$#" -lt 0 ]; then
#  usage
#  exit 1
#fi
#
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
        --force-repo-deletion)
            delete_repo="TRUE"; shift ;
            ;;
        --no-build)
            no_build="TRUE"; shift ;
            ;;
        uninstall)
            shift;
            uninstall
            exit 0
            ;;
        --kong)
            install_kong=1; shift;
            ;;
        feed-trace-analyzer)
            shift;
            feed_trace_analyzer "$@";
            exit 0
            ;;
        feed-stats)
            shift;
            feed_stats "$@";
            exit 0;
            ;;
        delete-pod-feed)
            shift;
            delete_pod_feed;
            exit 0;
            ;;
        --public-expose)
            shift;
            public_expose=true
            ;;
        respin-apiclarity)
            shift;
            uninstall_api_clarity --keep-namespace;
            install_apiclarity;
            echo "APIClarity has been completly respined"
            exit 0;
            ;;
        repush-apiclarity)
            shift;
            build_apiclarity
            uninstall_api_clarity --keep-namespace;
            install_apiclarity;
            echo "APIClarity has been reposhed and :qcompletly respined"
            exit 0;
            ;;
        *)
            break;
            exit 1
        esac
done

banner

if [[ ${delete_repo} == "TRUE" ]]; then
  read -p "Are you sure to delete apiclarity repo [y/N]?" yn
  if [[ ${yn} != "y" ]]; then
      echo "Remove --force-repo-deletion flag and run again. Bye!"
      exit 0
  fi
  rm -rf ${APICLARITY_FOLDER}
fi

if [[ ! -d ${APICLARITY_FOLDER} ]]; then
  git clone --single-branch --branch ${API_CLARITY_REPO_BRANCH} ${API_CLARITY_REPO} ${APICLARITY_FOLDER}
  (cd ${APICLARITY_FOLDER}; git submodule update --init --recursive)
  COMMIT_HASH=$(cd ${APICLARITY_FOLDER}; git rev-parse HEAD)
  sed -i '' 's/version: latest/version: 0.0/g' ${APICLARITY_FOLDER}/charts/apiclarity/Chart.yaml; 
  sed -i '' "s/image: ghcr.io\/openclarity\/kong-plugin:latest/image:  gcr.io\/eticloud\/scn-demo\/kong-plugin:${COMMIT_HASH}/g" ${APICLARITY_FOLDER}/plugins/gateway/kong/deploy/patch-deployment.yaml; 
fi

# Let's parallelize
echo "[+] Execute the following tasks in parallel"
echo "    [+] Building, pushing and installing APIClarity ..."
(build_apiclarity && install_apiclarity) > install_apiclarity.log 2>&1 &
echo "    [+] Installing Istio ..."
install_istio > install_istio.log 2>&1 &
echo "    [+] Installing sock-shop ..."
install_sock_shop > install_sock_shop.log 2>&1 &
echo "[+] Waiting for parallel processes to finish ..."
wait

echo "[+] Installing envoy filter"
install_envoy_filter > install_envoy_filter.log 2>&1

# Respin ALL sock shop pods. This is needed because as soon as envoy filter is
# installed, communication between pods is not working well anymore.
# XXX: Need to check why
echo "[+] Refreshing sock-shop pods"
kubectl --namespace sock-shop delete --all pods >> install_sock_shop.log 2>&1
# XXX Rollout doesn't solve the problem, pods really need to be deleted and recreated
# kubectl -n ${APP_NAMESPACE} rollout restart deploy
kubectl -n sock-shop wait --timeout=1m --for=condition=available deployment --all >> install_sock_shop.log 2>&1

final_message=$(cat <<EOF

    kubectl port-forward --namespace apiclarity svc/apiclarity-apiclarity 9999:8080
    kubectl port-forward --namespace sock-shop  svc/front-end 8079:80

    APIClarity: http://localhost:9999
    Sock-Shop:  http://localhost:8079

    You can generate Trace Analyzer traces with "./execute.sh feed-trace-analyzer 1"
    You can generate Stats traces with "./execute.sh feed-stats 1 /tmp/tools/provided_spec.json"

EOF
             )

if [ "${public_expose}" = true ] ; then
  echo "[+] Creating Public IP and LB"
  ip=$(reserve_static_ip);
  create_lb ${ip};
  final_message="${final_message}
    Services are publicly reachable at:

    - APIClarity: http://${ip}:9999
    - Sock-Shop:  http://${ip}:8079
"
fi

if [[ ! -z ${install_kong} ]]; then
  echo "[+] Installing and configuring kong gateway"
  global_kong_ip=""
  install_kong_and_api_clarity_plugin > install_kong.log 2>&1
  final_message="${final_message}

    * Kong Gateway has been installed
      IP: ${global_kong_ip}
"
fi

instructions "${final_message}"
