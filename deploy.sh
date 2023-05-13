#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

echo "> Starting Minikube"
minikube start --kubernetes-version=v1.22.0 HTTP_PROXY=https://minikube.sigs.k8s.io/docs/reference/networking/proxy/ --extra-config=apiserver.service-node-port-range=6000-32767 disk=20000MB --vm=true --driver=none

echo "> Enabling Nginx Ingress Controller"
minikube addons enable ingress

sleep 5

echo "> Installing openfaas"
arkade install openfaas --basic-auth-password password123 --set=faasIdler.dryRun=false

echo "> Waiting until openfaas gateway is ready"
kubectl rollout status -n openfaas deploy/gateway

sleep 5

echo "> Port forwarding for openfaas gateway"
kubectl port-forward -n openfaas svc/gateway 8080:8080 --address=0.0.0.0 &

echo "> Waiting until Openfaas to launch on 8080"
while ! nc -z localhost 8080; do
	sleep 1
done

sleep 5

echo "> Logging in to faas-cli"
PASSWORD=$(kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo)
echo -n $PASSWORD | faas-cli login --username admin --password-stdin
# faas-cli login --username admin --password password123

sleep 5

echo "> Deploying openfaas functions"
cd ${SCRIPT_DIR}/faas
faas-cli template store pull python3-http
faas-cli deploy -f stack.yml

echo "> Deploying mongodb"
kubectl apply -f ${SCRIPT_DIR}/mongodb.yml

echo "> Port forwarding for mongodb-service"
kubectl port-forward -n openfaas-fn svc/mongodb-service 27017:27017 --address=0.0.0.0 &

echo "> Deploying frontend"
kubectl apply -f ${SCRIPT_DIR}/frontend-deployment.yml
kubectl apply -f ${SCRIPT_DIR}/frontend-service.yml

echo "> Deploying NGINX Ingress Controller "
kubectl apply -f ingress.yml

# done
echo ">>>>>> Now you can visit our serverless application at:http://"${SERVER_IP}


