# Galaxy Helm Charts

This repo contains [Helm charts](https://helm.sh/) for easily deploying Galaxy on top of Kubernetes, in a number of scenarios, as described below.

## Requirements

- Helm installed: Please follow official instructions from [here] (https://github.com/helm/helm/blob/master/docs/install.md#installing-the-helm-client).
- Access to a Kubernetes cluster (with shared file system accessible through a Persistent Volume or equivalent).
  - For development purposes or local tests, the local Minikube environment can be used. Install minikube following [official instructions](https://kubernetes.io/docs/tasks/tools/install-minikube/).
- kubectl cli: The command line argument for connection to a Kubernetes instance (remote cluster or local minikube). If not installed as part of Minikube steps, follow ONLY the installation steps (not the configuration ones) from [here]( https://kubernetes.io/docs/tasks/tools/install-kubectl/).

## Minikube

If using minikube, you need to make sure that it is running. If you just installed it, you need to execute `minikube start`. In general you can check the status of minikube through `minikube status`.

## First time installation

If using helm for the first time, you will need to initialize the helm on the cluster and add the helm repo to the local helm directories:

```
$ helm init
$ helm list # call a few times until no error is shown, this is to wait for the tiller pod from helm to be running on the cluster.
$ helm repo add galaxy-helm-repo https://pcm32.github.io/galaxy-helm-charts
```

if you have done this once in the past, you might need, from time to time, to update the local repo, by doing:

```
$ helm repo update
```
  
## Available Helm Charts

The main Galaxy chart is `galaxy-stable`, where the `galaxy` chart will be soon deprecated. The `galaxy-stable` chart follows the production installation of Galaxy and relies as much as possible on the Galaxy docker-stable community images. You should be using version 2.0 and above of the `galaxy-stable` chart.

While the `galaxy` chart tends to use a much simpler and lightweight container setup, the `galaxy-stable` chart uses a more robust setup for the web part which allows the Galaxy web part to scale better. It also provides ftp upload support not available on the `galaxy` chart. The `galaxy-stable` chart also aims to use main Galaxy community images.

### `galaxy-stable` chart documentation

`galaxy-stable` chart is meant for running based on the docker-stable compose images, see [documentation](README-galaxy-stable.md).

### `galaxy` chart documentation

`galaxy` chart is meant to be used following the PhenoMeNal Galaxy container setup, see [documentation](README-galaxy.md).


# Funding

Most of this work, includng the Galaxy-Kubernetes integration, has been contributed to the community thanks to the funding of the European Comission (EC), through the PhenoMeNal H2020 Project, grant agreement number 654241.
