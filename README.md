[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/Ha6DivV4)

CSIT6000o Project - Serverless To Do List Application

| Name    | SID      | ITSC   | CONTRIBUTION                                                 |
| ------- | -------- | ------ | ------------------------------------------------------------ |
| PAN Han | 20881280 | hpanan | Openfaas functions, Replace DynamoDB with MongoDB， Kubernetes deployment, Automation scripts |
|         |          |        | Modified and built frontend service                          |
|         |          |        |                                                              |
|         |          |        |                                                              |

## Background

This project derives from the serverless web application from AWS Sample: https://github.com/aws-samples/lambda-refarch-webapp. We use OpenFaas to replace AWS Lambda functions, MongoDB to replace AWS DynamoDB and Nginx to replace AWS API Gateway.

## Infrastructure

The project is ready for deployment to a kubernetes cluster. To make the deployment simple enough, we build some automation script to deploy the project to a single-node Minikube cluster built on an AWS EC2 machine. The EC2 instance should expose the HTTP port 80 for frontend web application and port 8080 for OpenFaas functions. The deployments include a MongoDB database, several OpenFaas functions and a React Frontend application. All of these are deployed to the same namespace in the Kubernetes cluster: openfaas-fn. The infrastructure is illustrated by the figure below:

此处应有图。

## Deploy to an AWS EC2 instance

For the test machine, we choose the following config:

|               |                                        |
| ------------- | -------------------------------------- |
| OS            | Ubuntu Server 22.04 TLS                |
| Architecture  | 64-bit(x86)                            |
| Instance Type | M5.large                               |
| Network       | Public Subnet with public IP           |
| SG            | TCP Ports: 22, 80, 8080 From: Anywhere |
| Storage       | 30GiB gp3 on Root volume               |

> **After the deployment, all the Openfaas functions can be accessed through {server_ip}:31112/ui/. The mongodb database can be accessed through {server_ip}:27017 with compass.And the Frontend Web App can be accessed through http://{server_ip}**

## Manual Deployment

### Setup

To setup the environment, some packages need to be installed.

| Package   | Description                                                  |
| --------- | ------------------------------------------------------------ |
| minikube  | Single-node local k8s cluster                                |
| kubectl   | CLI to control k8s cluster                                   |
| docker    | All the components of the project is deployed as Docker images |
| socat     | Support port forwarding to expose service of k8s cluster     |
| conntrack | Support starting Minikube with none driver                   |
| arkade    | Marketplace for Openfaas in k8s                              |
| faas-cli  | CLI to build/delpoy openfaas functions                       |

Installation Commands:

> **_NOTE:_** These commands are only tested on Ubuntu 22.04 TLS platform
> Minikube:

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

Kubectl:

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

Docker:

```bash
sudo apt-get update && sudo apt-get install docker.io -y
```

Socat:

```bash
sudo apt-get install socat -y
```

Conntrack:

```bash
sudo apt-get install -y conntrack
```

Arkade:

```bash
curl -sLS https://get.arkade.dev | sudo sh
```

Faas-cli:

```bash
curl -sL https://cli.openfaas.com | sudo sh
```

### Deploy

> **_NOTE:_** **This part needs to be run as the root user**
>
> sudo -i

#### Step 1: Start Minikube

```bash
minikube start --kubernetes-version=v1.22.0 HTTP_PROXY=https://minikube.sigs.k8s.io/docs/reference/networking/proxy/ --extra-config=apiserver.service-node-port-range=6000-32767 disk=20000MB --vm=true --driver=none
```

Sometimes minikube fails to start. `minikube delete` can helps.

#### Step 2: Deploy Openfaas

```bash
arkade install openfaas --set=faasIdler.dryRun=false
```

This simple command will install openfaas but it will generate random password.

You can always use the following command to get the admin password for openfaas.

```
echo $(kubectl -n openfaas get secret basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode)
```

Here is another few commands to install openfaas. I prefer this, but it is a little complex. You can set you own user and password.

```bash
git clone https://github.com/openfaas/faas-netes
cd faas-netes
kubectl apply -f namespaces.yml
kubectl -n openfaas create secret generic basic-auth \
    --from-literal=basic-auth-user=admin \
    --from-literal=basic-auth-password=password123
kubectl apply -f ./yaml/
```

The user and password is used for `faas-cli` to login later. 

#### Step 3: Deploy Mongodb

```bash
cd todolist
```

```bash
kubectl apply -f ${REPO_HOME}/mongodb.yml
```

An mongodb-service is created in openfaas-fn namespace.

**Visualize MongoDB**

If you want to visualize the MongoDB, you can install [MongoDB Compass](https://www.mongodb.com/products/compass). This is not necessary.

Port-forward for MongoDB to port 27017.

```
kubectl port-forward -n openfaas-fn svc/mongodb-service 27017:27017 --address=0.0.0.0 &
```

 A port forwarding is necessary so that the MongoDB Compass can access through http://{server_ip}:27017. Ensure the mongodb-service is ready before running this command. And always run this command in the background to keep it from occupying the terminal.

Here is the string to connect to the MongoDB.

```bash
mongodb://admin:admin@{server_ip}:27017/?authMechanism=DEFAULT
```

After connection, you can see

![image-20230513164917907](C:\Users\Alice\AppData\Roaming\Typora\typora-user-images\image-20230513164917907.png)

#### Step 4: Deploy Openfaas Functions

Login in faas-cli

```bash
export OPENFAAS_URL=54.221.132.100 
faas-cli login -u admin -p password123 --gateway http://54.221.132.100:31112
```

```bash
cd faas
```

OpenFaaS does not have a default python template, so pull the template it first. Then, compile the yml, push it to docker, and then pull down from docker to deploy.

```bash
faas-cli template store pull python3-http
faas-cli build -f stack.yml
faas-cli push -f stack.yml
faas-cli deploy -f stack.yml --gateway http://{server_ip}:31112
```

Then you can access http://{server_ip}:31112 to test the backend service.

If you get an error, you can use this command to see the log.

```bash
faas-cli logs {function_name} --gateway http://{server_ip}:31112
```

Port-forward for Openfaas Gateway to port 8080.

```
kubectl port-forward -n openfaas svc/gateway 8080:8080 --address=0.0.0.0 &
```

An Openfaas gateway service(svc/gateway) is created on openfaas deployment in openfaas namespace, a port forwarding is necessary so that the openfaas functions can be accessed through {server_ip}:8080/function/{function_name}. Ensure the gateway service is ready before running this command. And always run this command in the background to keep it from occupying the terminal.








> **After the deployment, all the Openfaas functions can be accessed through {server_ip}:31112/ui/. And the Frontend Web App can be accessed through http://{server_ip}**





参考：

MongoDB：

https://blog.csdn.net/majiayu000/article/details/126491116

https://blog.csdn.net/qq_28550263/article/details/119892582

https://www.panyanbin.com/article/c602b9e2.html

https://juejin.cn/post/6844903597465927694

https://blog.alexellis.io/serverless-databases-with-openfaas-and-mongo/

openfass：

https://mfarache.github.io/mfarache/Url-Shortener-with-openfaas/

https://www.jianshu.com/p/6575a29840fd

https://blog.csdn.net/qq_30038111/article/details/113902683

https://blog.51cto.com/u_15064632/4317062

https://blog.csdn.net/qq_30038111/article/details/113902683

https://zhuanlan.zhihu.com/p/601314424

https://segmentfault.com/a/1190000023702396




#### Step 5: Deploy Frontend

```bash
kubectl apply -f ${REPO_HOME}/frontend.yml
```

Ensure the openfaas deployment finished and a namespace `openfaas-fn` exists before deploying the frontend app.

#### Step 6: Port-forward for Frontend Web App

```bash
kubectl port-forward -n openfaas-fn svc/frontend-service 80:8080 --address=0.0.0.0 &
```

An frontend service(`svc/frontend-service`) is created on frontend deployment in `openfaas-fn` namespace, a port forwarding is necessary so that the web application can be accessed through `http://{server_ip}`. Ensure the frontend service is ready before running this command. And always run this command in the background to keep it from occupying the terminal.