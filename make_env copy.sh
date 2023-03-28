#!/bin/bash
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo apt-get install kind
sudo apt-get install kubectl
sudo apt-get install helm

kind create cluster --name demo --config kind-config.yaml --image="kindest/node:v1.23.10@sha256:f047448af6a656fae7bc909e2fab360c18c487ef3edc93f06d78cdfd864b2d12"
kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.24.1/manifests/tigera-operator.yaml
kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.24.1/manifests/custom-resources.yaml

# install istio environment
curl -L https://istio.io/downloadIstio | sh -
export PATH=$PWD/bin:$PATH
istioctl install --set profile=demo -y

# install sock-shop (vulnerable webshop) environment
kubectl create namespace sock-shop
kubectl label namespaces sock-shop istio-injection=enabled
kubectl apply -f  ~/Documents/Anomaly-Detection-in-API-calls/scn-demo-master/test-apps/sock-shop/deploy/kubernetes/sock-shop.yaml

# install api clarity
helm repo add apiclarity https://openclarity.github.io/apiclarity
cd ~/Documents/Anomaly-Detection-in-API-calls/apiclarity

# install istio filters
git submodule init wasm-filters
git submodule update wasm-filters
cd wasm-filters


#./deploy.sh sock-shop
#cd Documents/Master AI/Thesis
kubectl rollout restart -f Documents/Anomaly-Detection-in-API-calls/scn-demo-master/test-apps/sock-shop/deploy/kubernetes/sock-shop.yaml 
