# Galaxy Helm Chart (v3)

[Galaxy](https://galaxyproject.org/) is a data analysis platform focusing on
accessibility, reproducibility, and transparency of primarily bioinformatics
data. This repo contains [Helm charts](https://helm.sh/) for easily deploying
Galaxy on top of Kubernetes.

You may [follow this documentation](https://galaxyproject.org/cloud/k8s/) on
how to use this Helm chart to deploy Galaxy on various managed kubernetes 
services (e.g., Amazon EKS and Google GKE).

## HELM 2 NOTE

Support for Helm 2 has been discontinued and users must upgrade to [Helm 3](https://helm.sh) to use these charts.

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
helm install my-galaxy-release-2 cloudve/galaxy --set cvmfs.enabled=true --set ingress.path="/galaxy2/"
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

| Parameters                                | Description                                                  |
| ----------------------------------------- | ------------------------------------------------------------ |
| `nameOverride`                            | Override the name of the chart used to prefix resource names. Defaults to `{{.Chart.Name}}` (i.e. `galaxy`) |
| `fullnameOverride`                        | Override the full name used to prefix resource names. Defaults to {{.Release.Name}}-{{.Values.nameOverride}} |
| `image.repository`                        | The repository and name of the Docker image for Galaxy, searches Docker Hub by default |
| `image.tag`                               | Galaxy Docker image tag (generally corresponds to the desired Galaxy version) |
| `image.pullPolicy`                        | Galaxy image [pull policy](https://kubernetes.io/docs/concepts/configuration/overview/#container-images) for more info |
| `imagePullSecrets`                        | Secrets used to [access a Galaxy image from a private repository](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/) |
| `service.type`                            | Kubernetes [Service type](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) |
| `service.port`                            | Kubernetes service port                                      |
| `service.nodePort`                        | If `service.type` is set to `NodePort`, then this can be used to set the port at which Galaxy will be available on all nodes' IP addresses |
| `workflowHandlers.*`                      | Configuration for the workflowHandlers (See below for all options) |
| `webHandlers.*`                           | Configuration for the webHandlers                            |
| `jobHandlers.*`                           | Configuration fo the jobHandlers                             |
| `jobHandlers.priorityClass.enabled`       | Assign a [priorityClass](https://kubernetes.io/docs/concepts/configuration/pod-priority-preemption/#priorityclass) to this handler. |
| `jobHandlers.priorityClass.existingClass` | The [priorityClass](https://kubernetes.io/docs/concepts/configuration/pod-priority-preemption/#priorityclass) to assign. |
| `metrics.enabled`                         | Enable metrics gathering.  The influxdb setting must be specified when using this setting.                                  |
| `metrics.image.repository`                | The location of the [galay-metrics-scraping](https://github.com/CloudVE/galaxy-docker-k8s-metrics) image to use. |
| `metrics.image.tag`                       | The image version to use.                                    |
| `metrics.image.pullPolicy`                | Define the [pull policy](https://kubernetes.io/docs/concepts/containers/images/#updating-images), that is, when Kubernetes will pull the image. |
| `serviceAccount.create`                   | The serviceAccount will be created if it does not exist.     |
| `serviceAccount.name`                     | The serviceAccount account to use.                           |
| `rbac.enabled`                            | Enable Galaxy job RBAC. This will grant the service account the necessary permissions/roles to view jobs and pods in this namespace. Defaults to true.  |
| `securityContext.fsGroup`                 | The [group](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) for any files created. |
| `persistence.enabled`                     | Enable persistence using PVC                                 |
| `persistence.name`                        | Name of the PVC                                              |
| `persistence.accessMode`                  | PVC access mode for the Galaxy volume                        |
| `persistence.size`                        | PVC storage request for the Galaxy volume, in GB             |
| `persistence.mountPath`                   | Path where to mount the Galaxy volume                        |
| `extraInitCommands`                       | Extra commands that will be run during initialization.       |
| `extraEnv`                                | Environment variables that will be defined                   |
| `ingress.enabled`                         | Enable Kubernetes ingress                                    |
| `ingress.canary.enabled`                  | This will create an additional ingress for detecting activity on Galaxy. Useful for autoscaling on activity. |
| `ingress.annotations.*`                   | Annotations that can be defined to configure an ingress controller. |
| `ingress.path`                            | Path where Galaxy application will be hosted                 |
| `ingress.hosts`                           | Hosts for the Galaxy ingress                                 |
| `ingress.tls`                             | Ingress configuration with HTTPS support                     |
| `resources.requests.cpu`                  | The requested amount of CPU (as time or number of cores)     |
| `resources.requests.memory`               | The requested amount of memory.                              |
| `resources.requests.ephemeral-storage`    | The requested amount of ephemeral storage                    |
| `resources.limits.cpu`                    | The maximum CPU that can be alloacted.                       |
| `resources.limits.memory`                 | The maximum memory that can be allocated.                    |
| `resources.limits.ephemeral-storage`      | The maximum ephemeral storage that can be allocated.         |
| `tolerations`                             | Define the `taints` that are tolerated.                      |
| `postgresql.enabled`                      | Enable the postgresql condition in the [requirements.yml](https://github.com/galaxyproject/galaxy-helm/blob/master/galaxy/requirements.yaml). |
| `cvmfs.enabled`                           | Enable CVMFS.                                                |
| `cvmfs.deploy`                            | Sets the `cvmfs.deploy` condition in the [requirements.yml](https://github.com/galaxyproject/galaxy-helm/blob/master/galaxy/requirements.yaml). |
| `useSecretConfigs`                        | Enable Kubernetes Secrets for all config maps                |
| `configs.*`                               | Galaxy configuration files and values for each of the files. The provided value represent the entire content of the given configuration file |
| `jobs.rules`                              | Galaxy dynamic job rules                                     |
| `extraFileMappings.*`                     | Map arbitrary files as configMaps or Secrets into any of the handlers |
| `influxdb.enabled`                        | Enable the `influxdb` used by the metrics scraper.           |
| `influxdb.url`                            | The connection URL to in the `influxdb`                      |
| `influxdb.username`                       | Influxdb user name.                                          |
| `influxdb.password`                       | Password for the influxdb user.                              |
| `nginx.image.repository`                  | Where to obtain the Nginx container.                         |
| `nginx.image.tag`                         | The Nginx version to pull.                                   |
| `nginx.image.pullPolicy`                  | When Kubernetes will [pull](https://kubernetes.io/docs/concepts/containers/images/#updating-images) the Nginx image from the repository. |
| `nginx.conf.client_max_body_size`         | Requests larger than this size will result in a `413 Payload Too Large`. |

# Handlers

Galaxy defines three handler types: `jobHandlers`, `webHandlers`, and `workflowHandlers`.  All three handler types share common configuration options.

| Parameter        | Description                                                  |
| :--------------- | :----------------------------------------------------------- |
| `replicaCount`   | The number of handlers to be spawned.                        |
| `livenessProbe`  | Probe used to determine if a pod should be restarted.        |
| `readinessProbe` | Probe used to determine if the pod is ready to accept workloads. |

## Liveness and Readiness Probes

Kubernetes uses `livenessProbe`s and `readinessProbe`s to determine the state of a pod.  Pods that fail the `livenessProbe` will be restarted and work will not be dispatched to the pod until the `readinessProbe` returns true.  A pod is `ready` when all of its containers are `ready`.

Liveness and readiness probes share the same configuration options.

| Parameter             | Description                                                  |
| :-------------------- | :----------------------------------------------------------- |
| `enabled`             | Enable/Disable the probe                                     |
| `initialDelaySeconds` | How long to wait before starting the probe.                  |
| `periodSeconds`       | How frequently Kubernetes with check the probe.              |
| `failureThreshold`    | The number of failures Kubernetes will retry the readiness probe before giving up. |
| `timeoutSeconds`      | How long Kubernetes will wait for a  probe to timeout.       |

### Examples

```
jobHandlers:
  replicaCount: 2
  livenessProbe: 
    enabled: false
  readinessProbe:
    enabled: true
    initialDelaySeconds: 300
    periodSecods: 30
    timeoutSeconds: 5
    failureThreshhold: 3
```



## Setting Parameters on the Command Line

Specify each parameter using the `--set key=value[,key=value]` argument to
`helm install`. For example,

```console
helm install galaxy --set persistence.size=50 .
```

The above command sets the Galaxy persistent volume to 50GB.

Setting Galaxy configuration file values requires the key name to be escaped:

```console
helm install --set-file "configs.galaxy\.yml.brand"="Hello World" galaxy
```

You can also set the galaxy configuration file in its entirety with:

```console
helm install --set-file "configs.galaxy\.yml"=/path/to/local/galaxy.yml galaxy
```

To unset an existing file and revert to the container's default version:

```console
helm install --set-file "configs.job_conf\.xml"=null galaxy
```

Alternatively, a YAML file that specifies the values of the parameters can be
provided when installing the chart. For example,

```console
helm install galaxy -f values-cvmfs.yaml .
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
helm install cvmfs --namespace cvmfs cloudve/galaxy-cvmfs-csi
# Download values-cvmfs.yaml from this repo and update persistence as needed
helm install galaxy cloudve/galaxy -f values.yaml --set cvmfs.enabled=true --set cvmfs.deploy=false
```

If you wish to get a quick deployment of a single Galaxy instance with its own
CVMFS-CSI, you can do so by enabling the CVMFS deployment as part of this chart:

```console
helm repo add cloudve https://raw.githubusercontent.com/CloudVE/helm-charts/master/
helm repo update
kubectl create namespace cvmfs
helm install cvmfs --namespace cvmfs cloudve/galaxy-cvmfs-csi
# Download values-cvmfs.yaml from this repo and update persistence as needed
helm install galaxy cloudve/galaxy -f values.yaml --set cvmfs.enabled=true --set cvmfs.deploy=true
```

If you use the latter method, it is highly recommended that you deploy a single
Galaxy release per nodepool, as multiple CVMFS-CSI provisioners running on the
same node can cause conflicts.

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
