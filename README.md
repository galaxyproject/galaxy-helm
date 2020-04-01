# Galaxy Helm Chart (v3)

[Galaxy](https://galaxyproject.org/) is a data analysis platform focusing on
accessibility, reproducibility, and transparency of primarily bioinformatics
data. This repo contains [Helm charts](https://helm.sh/) for easily deploying
Galaxy on top of Kubernetes.


You may [follow this documentation](https://galaxyproject.org/cloud/k8s/) on
how to use this Helm chart to deploy Galaxy on various managed kubernetes 
services (e.g., Amazon EKS and Google GKE). 

## TL;DR

```console
git clone https://github.com/galaxyproject/galaxy-helm.git
cd galaxy-helm/galaxy
helm dependency update
helm install .
```

## Introduction

This [Helm chart]() bootstraps a Galaxy deployment on a
[Kubernetes](https://kubernetes.io/) cluster. The chart allows application
configuration changes, updates, upgrades, and rollbacks.

## Prerequisites

- Kubernetes 1.13+
- Helm 2.10+

You will need a Kubernetes and Helm installation; the easiest option for
testing and development purposes is to install
[Docker Desktop](https://www.docker.com/products/docker-desktop), which comes
with integrated Kubernetes. You will also need to install
[Helm](https://github.com/helm/helm#install).

## Dependency Charts

This chart relies on the features of other charts for common functionality.
Most notably, this includes the Postgres chart for the database. In addition,
the chart relies on the use of the CVMFS chart for linking the reference data
to Galaxy and jobs. While, technically, CVMFS is an optional dependency,
production settings will likely want it enabled.

- Postgres
- CVMFS (optional)

## Installing the Chart

1. Clone this repository and install the required dependency charts.

```console
git clone https://github.com/galaxyproject/galaxy-helm.git
cd galaxy-helm/galaxy
helm dependency update
```

2. To install the chart with the release name `galaxy` (note the trailing dot):

```console
helm install --name galaxy .
```

In about a minute, Galaxy will be available at the root URL of your kubernetes
cluster.

## Uninstalling the Chart

To uninstall/delete the `galaxy` deployment, run:

```console
helm del --purge galaxy
```

## Configuration

The following table lists the configurable parameters of the Galaxy chart. The
current default values can be found in `values.yaml` file.

| Parameter                               | Description                                                                                                                                   |
|-----------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| `image.repository`                      | The repository and name of the Docker image for Galaxy pointing to Docker Hub.                                                                |
| `image.tag`                             | Galaxy image tag / version                                                                                                                    |
| `image.pullPolicy`                      | Galaxy image pull policy                                                                                                                      |
| `service.type`                          | Kubernetes Service type, ClusterIP by default.                                                                                                |
| `service.port`                          | Galaxy service port                                                                                                                          |
| `service.nodePort`                      | If `service.type` set to `NodePort`, then this can be used to set the port at which Galaxy will be available on all nodes' IP addresses. `30700` by default.                                                                                                            |
| `webHandlers.replicaCount`              | The number of replicas for the Galaxy web handlers                                                                                            |
| `jobHandlers.replicaCount`              | The number of replicas for the Galaxy job handlers                                                                                            |
| `rbac.enabled`                          | Enable Galaxy job RBAC                                                                                                                        |
| `persistence.enabled`                   | Enable persistence using PVC                                                                                                                  |
| `persistence.name`                      | Name of the PVC                                                                                                                               |
| `persistence.storageClass`              | PVC Storage Class for Galaxy volume (use either this or `existingClaim`)                                                                      |
| `persistence.existingClaim`             | An existing PVC to be used for the Galaxy volume (use either this or `storageClass`)                                                          |
| `persistence.accessMode`                | PVC access mode for the Galaxy volume                                                                                                         |
| `persistence.size`                      | PVC storage request for the Galaxy volume, in GB                                                                                              |
| `persistence.mountPath`                 | Path where to mount the Galaxy volume                                                                                                         |
| `extraEnv     `                         | Any extra environment variables you would like to pass on to the pod                                                                          |
| `ingress.enabled`                       | Enable Kubernetes ingress                                                                                                                     |
| `ingress.path`                          | Path where Galaxy application will be hosted                                                                                                  |
| `ingress.hosts`                         | Cluster hosts where Galaxy will be available                                                                                                  |
| `useSecretConfigs`                      | Enable Kubernetes Secrets for all config maps                                                                                                 |
| `configs.*`                             | Galaxy configuration files and values for each of the files. The provided value represent the entire content of the given configuration file  |
| `jobs.rules`                            | Galaxy dynamic job rules                                                                                                                      |
| `postgresql.galaxyDatabaseUser`         | Postgresql user for Galaxy database                                                                                                           |
| `postgresql.galaxyDatabasePassword`     | Password for Galaxy's postgresql user. This is not set by default and a random password is generated by Helm.                                                                                                       |
| `postgresql.galaxyExistingSecret`       | Overrides `galaxyDatabasePassword`. Use password from an exiting secret for Galaxy's postgresql user                                          |
| `postgresql.galaxyExistingSecretKeyRef` | Key for data portion containing the password from `galaxyExistingSecret`. Defaults to `galaxy-db-password`                                    |

Specify each parameter using the `--set key=value[,key=value]` argument to
`helm install`. For example,

```console
helm install --name galaxy --set persistence.size=50 .
```

The above command sets the Galaxy persistent volume to 50GB.

Setting Galaxy configuration file values requires the key name to be escaped:

```console
helm install --set-file "configs.galaxy\.yml.brand"="Hello World"
```

You can also set the galaxy configuration file in its entirety with:

```console
helm install --set-file "configs.galaxy\.yml"=/path/to/local/galaxy.yml
```

To unset an existing file and revert to the container's default version:

```console
helm install --set-file "configs.job_conf\.xml"=null
```

Alternatively, a YAML file that specifies the values of the parameters can be
provided when installing the chart. For example,

```console
helm install --name galaxy -f values-cvmfs.yaml .
```

To unset a config file, use the yaml null type:
```
configs:
  job_conf.xml: ~
 ```

## Data Persistence

The Galaxy Docker image stores all user data under `/galaxy/server/database`
path of the container. Persistent Volume Claims (PVCs) are used to keep the
data across deployments. It is possible to specify en existing PVC via
`persistence.existingClaim`. Alternatively, a value for
`persistence.storageClass` can be supplied to designate a desired storage
class for dynamic provisioning of the necessary PVCs. If neither value is
supplied, the default storage class for the k8s cluster will be used.

We recommend a storage class that supports `ReadWriteMany`, such as the
[nfs-provisioner](https://github.com/helm/charts/tree/master/stable/nfs-server-provisioner)
as the data must be available to all nodes in the cluster.

In addition, we recommend that you also set `postgresql.persistence.storageClass`
to a high-speed, durable storage type that is `ReadWriteOnce`, such as an EBS
volume.

## Note about persistent deployments and restarts

If you wish to make your deployment persistent or restartable (bring deployment down, keep the state in disk, then bring it up again later in time), you should create PVCs for Galaxy and Postgres and use the existingClaims variables to point to them as explained in the previous section. In addition, you MUST set the `postgresql.galaxyDatabasePassword` and `postgresql.postgresqlPassword` variables, as on a restart from the existing PVCs the Helm random password used for those slot won't be maintained, breaking database access.

To start a new deployment from PVCs that belonged to a previous deployment on a different cluster, you might need to disable the database init part by setting `postgresql.initdbScriptsSecrets: null`. 

### What if we didn't set db passwords in the first place

You can allow trusted local connections and then use that to enter the postgresql server and change passwords. To allow trusted connections, set the pg_hba.conf file through:

```
postgresql:
  pgHbaConfiguration: |
    host     all             all             0.0.0.0/0               md5
    host     all             all             ::1/128                 md5
    local    all             all                                     trust
```

## Production Settings

This repo contains an additional _values_ file with the production settings,
called `values-cvmfs.yaml`. This mode of deployment configures Galaxy
with the data from CMVFS and replicates the functional capabilities of the
[Galaxy Main server](usegalaxy.org). Note that this deployment mode does not
work on a Mac laptop because of an unresolved issue in the CVMFS-CSI docker
container.

To install this version of the chart, we first need to install the Galaxy 
CVMFS-CSI chart, followed by the Galaxy chart. Depending on the setup of
the cluster you have available, you may also need to supply values for the
cluster storage classes or PVCs.

```console
helm repo add cloudve https://raw.githubusercontent.com/CloudVE/helm-charts/master/
helm repo update
kubectl create namespace cvmfs
helm install --name cvmfs --namespace cvmfs cloudve/galaxy-cvmfs-csi
# Download values-cvmfs.yaml from this repo and update persistence as needed
helm install --name galaxy -f values-cvmfs.yaml cloudve/galaxy
```

Note that this setup takes several minutes to start due to Galaxy loading all
the tool definitions. Once started, Galaxy will be available under `/galaxy/`
(note the trailing `/` as it is required).

## Horizontal Scaling

The Galaxy application can be horizontally scaled for the web and job handlers
by setting the desired values of the `webHandlers.replicaCount` and
`jobHandlers.replicaCount` configuration options.

## Funding

- _Version 3_: Galaxy Project, Genomics Virtual Laboratory (GVL)

- _Version 2_: Genomics Virtual Laboratory (GVL), Galaxy Project, and European
  Commission (EC) H2020 Project PhenoMeNal, grant agreement number 654241.

- _Version 1_: European Commission (EC) H2020 Project PhenoMeNal, grant
  agreement number 654241.
