# Galaxy

[Galaxy](https://galaxyproject.org/) is a platform for bioinformatics data
analysis focusing on accessibility, reproducibility, and transparency.

## TL;DR;

```console
git clone https://github.com/CloudVE/galaxy-kubernetes.git
cd galaxy-kubernetes
helm dependency update
helm install .
```
In about a minute, Galaxy will be available at https://127.0.0.1/

## Introduction

This [Helm chart]() bootstraps a Galaxy deployment on a
[Kubernetes](https://kubernetes.io/) cluster. The chart allows application
configuration changes, updates, upgrades, and rollbacks.

## Prerequisites

- Kubernetes 1.10+
- Helm 2.13+

You will need a Kubernetes and Helm installation; the easiest option for
testing and development purposes is to install
[Docker Desktop](https://www.docker.com/products/docker-desktop), which comes
with integrated Kubernetes. You will also need to install
[Helm](https://github.com/helm/helm#install).

## Dependency Charts

This chart relies on the features of other charts for common functionality.
Most notably, this includes the Postgres chart for the database. In addition,
the chart relies on the use of the CVMFS chart for linking the reference data
to Galaxy and jobs. While technically the CVMFS is an optional dependency,
production settings will likely want to enable it.

- Postgres
- CVMFS (optional)

## Installing the Chart

1. Clone this repository and install the required dependency charts.
```
git clone https://github.com/CloudVE/galaxy-kubernetes.git
cd galaxy-kubernetes
helm dependency update
```

2. To install the chart with the release name `galaxy`:
```
helm install --name galaxy .
```
In about 50 seconds, Galaxy will be available at https://localhost/galaxy/.
Subsequent startup times are about 25 seconds.

## Uninstalling the Chart

To uninstall/delete the `galaxy` deployment, run:

```console
helm del --purge galaxy
```

## Configuration

The following table lists the configurable parameters of the Galaxy chart. The
current default values can be found in `values.yaml` file.

| Parameter                              | Description                                                                                                                                   |
|----------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| `image.repository`                     | The repository and name of the Docker image for Galaxy pointing to Docker Hub.                                                                |
| `image.tag`                            | Galaxy image tag / version                                                                                                                    |
| `image.pullPolicy`                     | Galaxy image pull policy                                                                                                                      |
| `nameOverride`                         |                                                                                                                                               |
| `fullnameOverride`                     |                                                                                                                                               |
| `service.type`                         | Kubernetes Service type                                                                                                                       |
| `service.port`                         | Galaxy service port                                                                                                                           |
| `webHandlers.replicaCount`             | The number of replicas for the Galaxy web handlers                                                                                            |
| `jobHandlers.replicaCount`             | The number of replicas for the Galaxy job handlers                                                                                            |
| `rbac.enabled`                         | Enable Galaxy job RBAC                                                                                                                        |
| `persistence.enabled`                  | Enable persistence using PVC                                                                                                                  |
| `persistence.name`                     | Name of the PVC                                                                                                                               |
| `persistence.storageClass`             | PVC Storage Class for Galaxy volume                                                                                                           |
| `persistence.accessMode`               | PVC access mode for the Galaxy volume                                                                                                         |
| `persistence.size`                     | PVC storage request for the Galaxy volume, in GB                                                                                              |
| `persistence.mountPath`                | Path where to mount the Galaxy volume                                                                                                         |
| `extraEnv.name`                        | Environment variables name to export in the Galaxy container                                                                                  |
| `extraEnv.value`                       | Environment variable values                                                                                                                   |
| `extraEnv.valueFrom.secretKeyRef.name` | Kubernetes Secrets service name with keys                                                                                                     |
| `extraEnv.valueFrom.secretKeyRef.key`  | Kubernetes Secrets service key with the environment variable value                                                                            |
| `ingress.enabled`                      | Enable Kubernetes ingress                                                                                                                     |
| `ingress.path`                         | Path where Galaxy application will be hosted                                                                                                  |
| `ingress.hosts`                        | Cluster hosts where Galaxy will be available                                                                                                  |
| `useSecretConfigs`                     | Enable Kubernetes Secrets for all config maps                                                                                                 |
| `configs.*`                            | Galaxy configuration files and values for each of the files. The provided value represent the entire content of the given configuration file. |
| `jobs.rules`                           | Galaxy dynamic job rules                                                                                                                      |

Specify each parameter using the `--set key=value[,key=value]` argument to
`helm install`. For example,

```console
helm install --name galaxy --set persistence.size=50 galaxy/galaxy
```

The above command sets the Galaxy persistent volume to 50GB.

Alternatively, a YAML file that specifies the values of the parameters can be
provided when installing the chart. For example,

```console
helm install --name galaxy -f values-production.yaml galaxy/galaxy
```

## Data Persistence

The Galaxy Docker image stores all user data under `/galaxy/server/database`
path of the container. Persistent Volume Claims (PVCs) are used to keep the
data across deployments.

## Production Settings

This repo contains an additional _values_ file with the production settings,
called `values-production.yaml`. This mode of deployment configures Galaxy
with the data from the CMVFS and replicates the functional capabilities of the
[Galaxy Main server](usegalaxy.org).

## Horizontal Scaling

The Galaxy application can be horizontally scaled for the web and job handlers
by setting the desired values of the `webHandlers.replicaCount` and
`jobHandlers.replicaCount` configuration options.
