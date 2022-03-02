# routines

Toy example of distributed workflow execution using Kubernetes and Celery


## setup

1. Download [Docker](https://minikube.sigs.k8s.io/docs/drivers/docker/)

  - may need to add user to docker group (can not run docker as root in kubernetes)

```
sudo usermod -aG docker $USER && newgrp docker
```

2. Download Kubernetes 

  - [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux)

  - [minikube](https://minikube.sigs.k8s.io/docs/start/)

## docker

### Build application components

The base image defines all requirements for the components. This `Dockerfile` is in the main project directory.

  - base image

```
sudo docker build . --tag apollodorus/routines-controller:v1
```

The following images provide entrypoints for the application components.

```
cd deployments/client && sudo docker build . --tag apollodorus/routines-api:v1
cd deployments/controller && sudo docker build . --tag apollodorus/routines-controller:v1
cd deployments/local-cluster && sudo docker build . --tag apollodorus/routines-local-cluster:v1
```

## local docker testing

1. Rabbitmq

```
sudo docker run -d --name rabbitmq --rm -p 5672:5672 rabbitmq:3.8-alpine
```

2. Celery

```
./docker/launch_local_cluster.sh
```

2. Controller 

```
./docker/launch_controller.sh
```

## Kubernetes

1.Start AMQP server 

 - RabbitMQ 

```
kubectl create -f deployments/rabbitmq/rabbitmq-service.yaml
```

2. Run deployment

```
kubectl apply -f ./deployments/deployment.yaml
```



