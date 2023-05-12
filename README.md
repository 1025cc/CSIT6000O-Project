[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/Ha6DivV4)

CSIT6000o Project - Serverless TODOList

| Name    | SID      | ITSC   | CONTRIBUTION                                                 |
| ------- | -------- | ------ | ------------------------------------------------------------ |
| PAN Han | 20881280 | hpanan | Openfaas functions, Kubernetes deployment, Automation scripts |
|         |          |        | Modified and built frontend service                          |
|         |          |        | Replace DynamoDB with MongoDB                                |
|         |          |        |                                                              |

## Background

This project derives from the serverless shopping cart project from AWS Sample: [https://github.com/aws-samples/aws-serverless-shopping-cart](https://github.com/aws-samples/aws-serverless-shopping-cart). We use Openfaas to replace AWS Lambda functions and MongoDB to replace AWS DynamoDB.

## Infrastructure

The project is ready for deployment to a kubernetes cluster. To make the deployment simple enough, we build some automation script to deploy the project to a single-node Minikube cluster built on an AWS EC2 machine. The EC2 instance should expose the HTTP port 80 for frontend web application and port 8080 for openfaas functions. The deployments include a MongoDB database, several openfaas functions and a JavaScript Vue Frontend application. All of these are deployed to the same namespace in the Kubernetes cluster: openfaas-fn. The infrastructure is illustrated by the figure below.

![](https://i.ibb.co/nDm3ZzL/infra-drawio-1.png)

## Deploy to an AWS EC2 instance

For the test machine, we choose the following config:

这个是openfaas的

|               |                                        |
| ------------- | -------------------------------------- |
| OS            | Ubuntu Server 20.04 TLS                |
| Architecture  | 64-bit(x86)                            |
| Instance Type | M5.large                               |
| Network       | Public Subnet with public IP           |
| SG            | TCP Ports: 22, 80, 8080 From: Anywhere |
| Storage       | 8GiB gp3 on Root volume                |

这个是MongoDB的

|               |                                        |
| ------------- | -------------------------------------- |
| OS            | Ubuntu Server 20.04 TLS                |
| Architecture  | 64-bit(x86)                            |
| Instance Type | M5.large                               |
| Network       | Public Subnet with public IP           |
| SG            | TCP Ports: 22, 80, 8080 From: Anywhere |
| Storage       | 16GiB gp3 on Root volume               |

> **After the deployment, all the Openfaas functions can be accessed through {server_ip}:31112/ui/. And the Frontend Web App can be accessed through http://{server_ip}**

![](https://i.ibb.co/w4Dc9MH/deploy.png)

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

Since we deploy the project to EC2 instance, here we choose not to use a driver for minikube. Sometimes minikube fails to start. A `minikube delete` is necessary before `minikube start --driver=none`. And the minikube will automatically configure kubectl, only if `kubectl` is installed ahead of `minikube start`. Please ensure `kubectl` is installed before running this command.

#### Step 2: Deploy Openfaas

这个命令我没跑通

```bash
arkade install openfaas --basic-auth-password admin --set=faasIdler.dryRun=false
```

#### 下面这个我可以跑通

```bash
git clone https://github.com/openfaas/faas-netes
cd faas-netes
kubectl apply -f namespaces.yml
kubectl -n openfaas create secret generic basic-auth \
    --from-literal=basic-auth-user=admin \
    --from-literal=basic-auth-password=admin
kubectl apply -f ./yaml/
```



Here we use a command line option `basic-auth-password` for simplicity, but this is a deprecated method. The password is used for `faas-cli` to login later. You can always use `kubectl -n openfaas get secret basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode` to get the admin password for openfaas.



#### Step 4: Deploy Mongodb


Mongodb包在默认的Ubuntu存储库中是不可使用的。首先需要导入包管理系统使用的公钥。

```bash
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
```

更新apt资源库

```bash
sudo apt update
sudo apt upgrade -y
```


创建列表文件

```bash
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

sudo apt update
```



#### 安装libssl

```bash
curl -LO http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1-1ubuntu2.1~18.04.22_amd64.deb
sudo dpkg -i ./libssl1.1_1.1.1-1ubuntu2.1~18.04.22_amd64.deb
```

安装mongodb

```bash
sudo apt install -y mongodb-org
```


安装完成后可以启动mongodb了

```bash
sudo systemctl start mongod  # start mongodb

sudo systemctl status mongod  # check status of mongodb
```



可以下载compass 查看数据库

需要新建账户

```bash
use admin
db.update("admin", {pwd: 'admin', roles:["dbAdminAnyDatabase", "readWriteAnyDatabase"]}
```

修改配置：

```bash
sudo vim /etc/mongod.conf
```



```bash
net:
  port: 27017
  bindIp: 0.0.0.0
```



其中：

- bindIp改为`0.0.0.0`，表示不限制ip访问，可远程通过软件访问，默认的配置值是`127.0.0.1`，即只能本机访问；







链接的string

```bash
mongodb://admin:admin@54.86.120.210:27017/?authMechanism=DEFAULT

mongodb://admin:admin@{server_ip}:27017/?authMechanism=DEFAULT
```

#### Step 7: docker部署

https://hub.docker.com/

要用的模块新建好，得到链接后，在stack.yml里面更新image对应的位置。

```bash
version: 1.0

provider:

 name: openfaas

 gateway: http://127.0.0.1:8080

functions:

 addtodo:

  lang: python3-http

  handler: ./addtodo

  image: panhan28/serverlesstodolist_addtodo:latest
```

#### 





#### Step 7: Deploy Openfaas Functions

登录

```bash
export OPENFAAS_URL={server_ip}
faas-cli login -u admin -p admin --gateway http://{server_ip}:31112

export OPENFAAS_URL=54.221.132.100 
faas-cli login -u admin -p admin --gateway http://54.221.132.100:31112
```

进入stack.yml的文件夹

```bash
cd ${REPO_HOME}/faas
```

openfaas没有默认的python模板，所以先pull

后面是编译，push到docker上，再从docker上拉下来部署。

```bash
faas-cli template store pull python3-http
faas-cli build -f stack.yml
faas-cli push -f stack.yml
faas-cli deploy -f stack.yml --gateway http://{server_ip}:31112
```



报错的话可以用这个命令

```bash
 faas-cli logs {function_name} --gateway http://{server_ip}:31112
```





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




Step 3: Port-forward for Openfaas Gateway

kubectl port-forward -n openfaas svc/gateway 8080:8080 --address=0.0.0.0 &

An Openfaas gateway service(svc/gateway) is created on openfaas deployment in openfaas namespace, a port forwarding is necessary so that the openfaas functions can be accessed through {server_ip}:8080/function/{function_name}. Ensure the gateway service is ready before running this command. And always run this command in the background to keep it from occupying the terminal.


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

