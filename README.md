# Galaxy Helm Charts

This repo contains [Helm charts]() for easily deploying Galaxy on top of Kubernetes, in a number of scenarios, as described below. The two minimal requirements to be able to use them are:
- Helm installed
- Access to a Kubernetes cluster
  - For development purposes or local tests, the local Minikube environment can be used.
  
## Available Helm Charts

Currently we have two separate helm charts: 

- `galaxy-simple` : aimed mostly at development enviroment, running on Minikube, although it can be run on other environments. It has only fixed support for sqlite. It has a number of options for filesystem provisioning, ingresses, container image to use, etc.
- `galaxy-postgres-chart` : aimed at production deployment, but can be as well installed locally on Minikube. It uses Postgres as a backend, and has many configurable options (secure the instance for a user, access through ip:port or DNS based, filesystem provisioning, etc).

We expect in the near future to unify both charts to reduce maintainance efforts.

## Helm for the first time

If using helm for the first time, you will need to initialize the helm on the cluster and add the helm repo to the local helm directories:

```
$ helm init
$ helm repo add galaxy-helm-repo https://pcm32.github.io/galaxy-helm-charts
```

if you have done this once in the past, you might need, from time to time, to update the local repo, by doing:

```
$ helm repo update
```
  
## Deployment scenarios

Here we show different examples on how to deploy Galaxy on Kubernetes with these helm charts for Galaxy. 

### Simple local deploy on Minikube

```
$ helm install --set pv_minikube="yes" galaxy-helm-repo/galaxy-simple
```

This will produce an instance accessible on the minukube ip, port 30700.


# Funding

Most of this work, includng the Galaxy-Kubernetes integration, has been contributed to the community thanks to the funding of the European Comission (EC), through the PhenoMeNal H2020 Project, grant agreement number 654241.
