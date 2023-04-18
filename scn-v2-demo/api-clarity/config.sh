set -e
set -x

GCP_PROJECT="gcp-etiappsecurity-nprd-62652"
#K8S_CONTEXT="gke_gcp-etigcp-nprd-12855_europe-west4-a_jubarbot-dev"
# K8S_CONTEXT="eks-szigeti-8"
K8S_CONTEXT="test-oreo"
#GCP_REGION="europe-west4"
GCP_REGION="us-central1"

APP_NAMESPACE="sock-shop"

GATEWAY_TYPE="KONG"
GATEWAY_TYPE="ENVOY"

##### Envoy #######
ISTIO_VERSION="1.13.0"

#### APICLARITY BUILDER ####
APICLARITY_BUILDER_REGISTRY=gcr.io/eticloud/k8sec
APICLARITY_BUILDER_REPO="git@github.com:cisco-eti/apiclarity-builder.git"
APICLARITY_BUILDER_BRANCH="main"
APICLARITY_BUILDER_FOLDER="apiclarity-builder-${APICLARITY_BUILDER_BRANCH}"


##### Api clarity ######
API_CLARITY_REPO="git@github.com:openclarity/apiclarity.git"
#API_CLARITY_REPO="git@wwwin-github.cisco.com:eti/apiclarity.git"
API_CLARITY_REPO_BRANCH="master"
# API_CLARITY_IMAGE_REGISTRY="gcr.io/gcp-etigcp-nprd-12855/demos"
API_CLARITY_IMAGE_REGISTRY="gcr.io/eticloud/scn-demo"

##### Api clarity plugin ######
# Those variables need to be exported because they are used by other subscripts
export KONG_GATEWAY_DEPLOYMENT_NAME="ingress-kong"
export KONG_GATEWAY_DEPLOYMENT_NAMESPACE="kong"
export KONG_GATEWAY_INGRESS_NAME="catalogue"
export KONG_GATEWAY_INGRESS_NAMESPACE="sock-shop"
export UPSTREAM_TELEMETRY_HOST_NAME="apiclarity-apiclarity.apiclarity"

export DOCKER_DEFAULT_PLATFORM=linux/amd64

##### Envoy ######
WASM_FILTER_TRACE_BACKEND_ADDRESS="apiclarity-apiclarity.apiclarity.svc.cluster.local"

##### Computed variables #####
BASE_DIR="$(pwd)/$(dirname ${BASH_SOURCE[0]})"
APP_PATH="${BASE_DIR}/../test-apps/sock-shop"
APP_PATH_MANIFEST="${APP_PATH}/deploy/kubernetes/sock-shop.yaml"
APICLARITY_FOLDER="apiclarity-${API_CLARITY_REPO_BRANCH}"

kubectl config use-context ${K8S_CONTEXT}
