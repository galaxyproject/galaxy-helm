# Galaxy Helm Chart (v3)

[Galaxy](https://galaxyproject.org/) is a data analysis platform focusing on
accessibility, reproducibility, and transparency of primarily bioinformatics
data. This repo contains [Helm charts](https://helm.sh/) for easily deploying
Galaxy on top of Kubernetes.


You may [follow this documentation](https://galaxyproject.org/cloud/k8s/) on
how to use this Helm chart to deploy Galaxy on various managed kubernetes 
services (e.g., Amazon EKS and Google GKE).

## HELM 2 NOTE

While the chart is still compatible with Helm 2, we highly recommend you start
using Helm 3 since we will not keep supporting Helm 2 going forward.
For Helm 2 installation, you will need to replace `helm install my-galaxy-release`
with `helm install --name my-galaxy-release` in all the commands below.

## Introduction

This [Helm chart](https://helm.sh/) bootstraps a Galaxy deployment on a
[Kubernetes](https://kubernetes.io/) cluster. The chart allows application
configuration changes, updates, upgrades, and rollbacks.

## Recommended versions

- Kubernetes 1.16+
- Helm 3+

You will need a Kubernetes and Helm installation; the easiest option for
testing and development purposes is to install
[Docker Desktop](https://www.docker.com/products/docker-desktop), which comes
with integrated Kubernetes. You will also need to
[install Helm](https://github.com/helm/helm#install).

## Dependency Charts

This chart relies on the features of other charts for common functionality.
Most notably, this includes the Postgres chart for the database. In addition,
the chart can rely on the use of the CVMFS-CSI chart for linking the reference data
to Galaxy and jobs. While, technically, CVMFS is an optional dependency,
production settings will likely want it enabled.

- Postgres
- [Galaxy-CVMFS-CSI](https://github.com/CloudVE/galaxy-cvmfs-csi-helm) (optional)


## TL;DR

### Default simple installation (with few basic tools)

Launching from the source:

```console
git clone https://github.com/galaxyproject/galaxy-helm.git
cd galaxy-helm/galaxy
helm dependency update
helm install my-galaxy-release .
```

Launching from the repository of packaged charts:

```console
helm repo add cloudve https://raw.githubusercontent.com/CloudVE/helm-charts/master/
helm repo update
helm install my-galaxy-release cloudve/galaxy
```

### Example installation for a single Galaxy instance with CVMFS tools

```console
helm repo add cloudve https://raw.githubusercontent.com/CloudVE/helm-charts/master/
helm repo update
helm install my-galaxy-release cloudve/galaxy --set cvmfs.enabled=true --set cvmfs.deploy=true
```

NOTE: It is not advisable to run multiple instances of the CVMFS-CSI simultaneously on
the same cluster. If you wish to deploy multiple instances of Galaxy on the same cluster,
please install the CVMFS-CSI chart separately as shown below. One exception to this is
installing multiple releases of Galaxy in different namespaces AND running on different
nodepools. In that case, it is possible to have each Galaxy release deploy its own 
CVMFS-CSI (and own NFS provisioner if desired). For that case, please refer to the
[GalaxyKubeMan Chart](https://github.com/galaxyproject/galaxykubeman-helm).

### Example installation for multiple Galaxy instances on the same cluster

```console
helm repo add cloudve https://raw.githubusercontent.com/CloudVE/helm-charts/master/
helm repo update
helm install cvmfs cloudve/galaxy-cvmfs-csi --namespace cvmfs --create-namespace
helm install my-galaxy-release-1 cloudve/galaxy --set cvmfs.enabled=true --set cvmfs.deploy=false --set ingress.path="/galaxy1/"
helm install my-galaxy-release-2 cloudve/galaxy --set cvmfs.enabled=true --set ingress.paht="/galaxy2/"
```
Note: `cvmfs.deploy` defaults to `false`. The explicit mention in the first release is
purely visual to highlight the difference.

## Installing the Chart

1. Clone this repository and install the required dependency charts.

```console
git clone https://github.com/galaxyproject/galaxy-helm.git
cd galaxy-helm/galaxy
helm dependency update
```

2. To install the chart with the release name `my-galaxy` (note the trailing dot):

```console
helm install my-galaxy .
```

In about a minute, Galaxy will be available at the root URL of your kubernetes
cluster.

## Uninstalling the Chart

To uninstall/delete the `galaxy` deployment, run:

```console
helm delete my-galaxy
```

## Configuration

The following table lists the configurable parameters of the Galaxy chart. The
current default values can be found in `values.yaml` file.

| Parameter                               | Description                                                                                                                                   |
|-----------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| `nameOverride`                          | Override the name of the chart used to prefix resource names. Defaults to `{{.Chart.Name}}` (i.e. `galaxy`)   |
| `fullNameOverride`                      | Override the full name used to prefix resource names. Defaults to `{{.Release.Name}}-{{.Values.nameOverride}}` |
| `image.repository`                      | The repository and name of the Docker image for Galaxy, searches Docker Hub by default                                                               |
| `image.tag`                             | Galaxy Docker image tag (generally corresponds to the desired Galaxy version)                                                                                                                    |
| `image.pullPolicy`                      | Galaxy image [pull policy](https://kubernetes.io/docs/concepts/configuration/overview/#container-images) for more info                |
| `service.type`                          | Kubernetes [Service type](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) |
| `service.port`                          | Kubernetes service port                                                                                                                          |
| `service.nodePort`                      | If `service.type` is set to `NodePort`, then this can be used to set the port at which Galaxy will be available on all nodes' IP addresses                                                                                                            |
| `webHandlers.replicaCount`              | The number of replicas for the Galaxy web handlers    |
| `webHandlers.annotations`               | Additional annotations for the Galaxy web handlers at the Deployment level  |
| `webHandlers.podAnnotations`              | Additional annotations for the Galaxy web handlers at the Pod level  |
| `webHandlers.podSpecExtra`              | Additional specs for the Galaxy web handlers at the pod level                                                         |
| `webHandlers.readinessProbe.enabled`      | The number of replicas for the Galaxy web handlers        |
|
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

This repo contains a values file that supports CVMFS support out-of-the-box.
This mode of deployment configures Galaxy with the data from CMVFS and
replicates the functional capabilities of the [Galaxy Main server](usegalaxy.org).
Note that this deployment mode does not work on a Mac laptop because of an 
unresolved issue in the CVMFS-CSI docker container.

To install this version of the chart, we need to enable CVMFS deployment.
Depending on the setup of the cluster you have available, you may also need
to supply values for the cluster storage classes or PVCs.

If you wish to install a single Galaxy CVMFS-CSI release to be used by multiple
Galaxy releases, you can do so by installing the CVMFS separately as shown below:

```console
helm repo add cloudve https://raw.githubusercontent.com/CloudVE/helm-charts/master/
helm repo update
kubectl create namespace cvmfs
helm install --name cvmfs --namespace cvmfs cloudve/galaxy-cvmfs-csi
# Download values-cvmfs.yaml from this repo and update persistence as needed
helm install --name galaxy cloudve/galaxy -f values.yaml --set cvmfs.enabled=true --set cvmfs.deploy=false
```

If you wish to get a quick deployment of a single Galaxy instance with its own
CVMFS-CSI, you can do so by enabling the CVMFS deployment as part of this chart:

```console
helm repo add cloudve https://raw.githubusercontent.com/CloudVE/helm-charts/master/
helm repo update
kubectl create namespace cvmfs
helm install --name cvmfs --namespace cvmfs cloudve/galaxy-cvmfs-csi
# Download values-cvmfs.yaml from this repo and update persistence as needed
helm install --name galaxy cloudve/galaxy -f values.yaml --set cvmfs.enabled=true --set cvmfs.deploy=true
```

If you use the latter method, it is highly recommended that you deploy a single
Galaxy release per nodepool, as multiple CVMFS-CSI provisioners running on the
same node can conflict.

Once started, Galaxy will be available under `/galaxy/` (note the trailing `/`).
This path can be changed by setting the value: `--set ingress.path="/mynewgalaxypath/"

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
