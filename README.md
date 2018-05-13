# Galaxy Helm Charts

This repo contains [Helm charts]() for easily deploying Galaxy on top of Kubernetes, in a number of scenarios, as described below. The two minimal requirements to be able to use them are:
- Helm installed
- Access to a Kubernetes cluster (with shared file system accessible through a Persistent Volume or equivalent).
  - For development purposes or local tests, the local Minikube environment can be used.

## Helm for the first time

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

Previously functionality was split in two charts, they have now been unified into the `galaxy` chart, which merges all functionality available on `galaxy-simple` and `galaxy-postgres-chart`, which are deprecated now. Newer features, such as privileged file system support, are only supported on the `galaxy` chart. The new `galaxy` chart can be used for development, testing and production environments and is highly configurable.

To make use of the docker-stable compose Galaxy images, a new chart named `galaxy-stable` was created. This one in turn will probably superseed the `galaxy` chart. 

While the `galaxy` chart tends to use a much simpler and lightweight container setup, the `galaxy-stable` chart uses a more robust setup for the web part which allows the Galaxy web part to scale better. It also provides ftp upload support not available on the `galaxy` chart. The `galaxy-stable` chart also aims to use main Galaxy community images.

### `galaxy-stable` chart documentation

`galaxy-stable` chart is meant for running based on the docker-stable compose images, see [documentation](README-galaxy-stable.md).

### `galaxy` chart documentation

`galaxy` chart is meant to be used following the PhenoMeNal Galaxy container setup, see [documentation](README-galaxy.md).


# Funding

Most of this work, includng the Galaxy-Kubernetes integration, has been contributed to the community thanks to the funding of the European Comission (EC), through the PhenoMeNal H2020 Project, grant agreement number 654241.
