# Galaxy Helm Chart (v4)

[Galaxy](https://galaxyproject.org/) is a data analysis platform focusing on
accessibility, reproducibility, and transparency of primarily bioinformatics
data. This repo contains [Helm charts](https://helm.sh/) for easily deploying
Galaxy on top of Kubernetes. The chart allows application configuration changes,
updates, upgrades, and rollbacks.

You may [follow this documentation](https://galaxyproject.org/cloud/k8s/) on
how to use this Helm chart to deploy Galaxy on various managed kubernetes
services (e.g., Amazon EKS and Google GKE).

## Recommended versions

- Kubernetes 1.16+
- Helm 3.5+

### Helm 2 note

Support for Helm 2 has been discontinued and users must upgrade to [Helm
3](https://helm.sh) to use these charts.

## Kubernetes cluster

You will need `kubectl` ([instructions](https://kubernetes.io/docs/tasks/tools/#kubectl))
and `Helm` ([instructions](https://helm.sh/docs/intro/install/)) installed.

In terms of getting a Kubernetes cluster, an easy option for testing and
development purposes is to install [Docker
Desktop](https://www.docker.com/products/docker-desktop), which comes with
integrated Kubernetes.

Another out-of-the box option is [`k3d`](https://k3d.io/) which runs a `k3s`
cluster.

_Note:_ The CVMFS-CSI driver used for reference data unfortunately does not work
on a Mac at the moment.

## Dependency charts

This chart relies on the features of other charts for common functionality:
- [postgres-operator](https://github.com/zalando/postgres-operator) for the
  database;
- [CVMFS-CSI chart](https://github.com/CloudVE/galaxy-cvmfs-csi-helm) for
  linking the reference data to Galaxy and jobs. While, technically, CVMFS is an
  optional dependency, production settings will likely want it enabled.

_Note:_ It is not advisable to run multiple instances of the CVMFS-CSI
simultaneously on the same cluster. If you wish to deploy multiple instances of
Galaxy on the same cluster, please install the CVMFS-CSI chart separately as
shown below. One exception to this is installing multiple releases of Galaxy in
different namespaces AND running on different nodepools. In that case, it is
possible to have each Galaxy release deploy its own CVMFS-CSI (and own NFS
provisioner if desired). For that case, please refer to the [GalaxyKubeMan
Chart](https://github.com/galaxyproject/galaxykubeman-helm).

In a production setting, especially if the intention is to run multiple Galaxies
in a single cluster, we recommend installing these charts separately once per
cluster, and installing Galaxy with `--set postgresql.deploy=false --set
cvmfs.deploy=false --set cvmfs.enabled=true`.

## TL;DR

### Default simple installation (with only a few basic Galaxy tools)

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

### Example installation for a single Galaxy instance with CVMFS

```console
helm repo add cloudve https://raw.githubusercontent.com/CloudVE/helm-charts/master/
helm repo update
helm install my-galaxy-release cloudve/galaxy --set cvmfs.enabled=true --set cvmfs.deploy=true
```

### Example installation for multiple Galaxy instances on the same cluster

```console
helm repo add cloudve https://raw.githubusercontent.com/CloudVE/helm-charts/master/
helm repo update
helm install cvmfs cloudve/galaxy-cvmfs-csi --namespace cvmfs --create-namespace
helm install my-galaxy-release-1 cloudve/galaxy --set cvmfs.enabled=true --set cvmfs.deploy=false --set ingress.path="/galaxy1/"
helm install my-galaxy-release-2 cloudve/galaxy --set cvmfs.enabled=true --set ingress.path="/galaxy2/"
```
_Note:_ `cvmfs.deploy` defaults to `false`. The explicit mention in the first release is
purely visual to highlight the difference.

## Installing the chart

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

In about a minute, Galaxy will be available at the root URL of your Kubernetes
cluster.

## Uninstalling the chart

To uninstall/delete the `galaxy` deployment, run:

```console
helm delete my-galaxy
```

## Configuration

The following table lists the configurable parameters of the Galaxy chart. The
current default values can be found in `values.yaml` file.

| Parameters                                 | Description                                                                                                                                                                                                |
|--------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `nameOverride`                             | Override the name of the chart used to prefix resource names. Defaults to `{{.Chart.Name}}` (i.e. `galaxy`)                                                                                                |
| `fullnameOverride`                         | Override the full name used to prefix resource names. Defaults to `{{.Release.Name}}-{{.Values.nameOverride}}`                                                                                             |
| `image.pullPolicy`                         | Galaxy image [pull policy](https://kubernetes.io/docs/concepts/configuration/overview/#container-images) for more info                                                                                     |
| `image.repository`                         | The repository and name of the Docker image for Galaxy, searches Docker Hub by default                                                                                                                     |
| `image.tag`                                | Galaxy Docker image tag (generally corresponds to the desired Galaxy version)                                                                                                                              |
| `imagePullSecrets`                         | Secrets used to [access a Galaxy image from a private repository](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/)                                                   |
| `persistence.enabled`                      | Enable persistence using PVC                                                                                                                                                                               |
| `persistence.size`                         | PVC storage request for the Galaxy volume, in GB                                                                                                                                                           |
| `persistence.accessMode`                   | PVC access mode for the Galaxy volume                                                                                                                                                                      |
| `persistence.annotations.{}`               | Dictionary of annotations to add to the persistent volume claim's metadata                                                                                                                                 |
| `persistence.existingClaim`                | Use existing Persistent Volume Claim instead of creating one                                                                                                                                               |
| `persistence.storageClass`                 | Storage class to use for provisioning the Persistent Volume Claim                                                                                                                                          |
| `persistence.name`                         | Name of the PVC                                                                                                                                                                                            |
| `persistence.mountPath`                    | Path where to mount the Galaxy volume                                                                                                                                                                      |
| `useSecretConfigs`                         | Enable Kubernetes Secrets for all config maps                                                                                                                                                              |
| `configs.{}`                               | Galaxy configuration files and values for each of the files. The provided value represent the entire content of the given configuration file                                                               |
| `jobs.priorityClass.enabled`               | Assign a [priorityClass](https://kubernetes.io/docs/concepts/configuration/pod-priority-preemption/#priorityclass) to the dispatched jobs.                                                                 |
| `jobs.rules`                               | Galaxy dynamic job rules. <a href="galaxy/values.yaml">See `values.yaml`</a>                                                                                                                                                                |
| `jobs.priorityClass.existingClass`         | Use an existing [priorityClass](https://kubernetes.io/docs/concepts/configuration/pod-priority-preemption/#priorityclass) to assign if `jobs.priorityClass.enabled=true`                                   |
| `cvmfs.deploy`                             | Deploy the Galaxy-CVMFS-CSI Helm Chart. This is an optional dependency, and for production scenarios it should be deployed separately as a cluster-wide resource                                           |
| `cvmfs.enabled`                            | Enable use of CVMFS in configs, and deployment of CVMFS Persistent Volume Claims for Galaxy                                                                                                                |
| `cvmfs.galaxyPersistentVolumeClaims.{}`    | Persistent Volume Claims to deploy for CVMFS repositories. <a href="galaxy/values.yaml">See `values.yaml`</a> for examples.                                                                                                                 |
| `initJob.ttlSecondsAfterFinished`          | Sets `ttlSecondsAfterFinished` for the initialization jobs. See the [Kubernetes documentation](https://kubernetes.io/docs/concepts/workloads/controllers/ttlafterfinished/#ttl-controller) for more details.       |
| `initJob.downloadToolConfs.enabled`        | Download configuration files and the `tools` directory from an archive via a job at startup                                                                                                                |
| `initJob.downloadToolConfs.archives.startup` | A URL to a `tar.gz` publicly accessible archive containing AT LEAST conf files and XML tool wrappers. Meant to be enough for Galaxy handlers to startup.                                                   |
| `initJob.downloadToolConfs.archives.running` | A URL to a `tar.gz` publicly accessible archive containing AT LEAST confs, tool wrappers, and tool scripts but excluding test data. Meant to be enough for Galaxy handlers to run jobs.                    |
| `initJob.downloadToolConfs.archives.full`  | A URL to a `tar.gz` publicly accessible archive containing the full `tools` directory, including each tool's test data. Meant to be enough to run automated tool-tests, fully mimicking CVMFS repositories |
| `initJob.downloadToolConfs.volume.mountPath` | Path at which to mount the unarchived confs in the each handler (should match path set in the tool confs)                                                                                                  |
| `initJob.downloadToolConfs.volume.subPath` | Name of subdirectory on Galaxy's shared filesystem to use for the unarchived configs                                                                                                                       |
| `initJob.createDatabase`                   | Deploy a job to create a Galaxy database from scratch (does not affect subsequent upgrades, only first startup)                                                                                            |
| `ingress.path`                             | Path where Galaxy application will be hosted                                                                                                                                                               |
| `ingress.annotations.{}`                   | Dictionary of annotations to add to the ingress's metadata at the deployment level                                                                                                                         |
| `ingress.hosts`                            | Hosts for the Galaxy ingress                                                                                                                                                                               |
| `ingress.canary.enabled`                   | This will create an additional ingress for detecting activity on Galaxy. Useful for autoscaling on activity.                                                                                               |
| `ingress.enabled`                          | Enable Kubernetes ingress                                                                                                                                                                                  |
| `ingress.tls`                              | Ingress configuration with HTTPS support                                                                                                                                                                   |
| `service.nodePort`                         | If `service.type` is set to `NodePort`, then this can be used to set the port at which Galaxy will be available on all nodes' IP addresses                                                                 |
| `service.port`                             | Kubernetes service port                                                                                                                                                                                    |
| `service.type`                             | Kubernetes [Service type](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types)                                                                              |
| `serviceAccount.annotations.{}`            | Dictionary of annotations to add to the service account's metadata                                                                                                                                         |
| `serviceAccount.create`                    | The serviceAccount will be created if it does not exist.                                                                                                                                                   |
| `serviceAccount.name`                      | The serviceAccount account to use.                                                                                                                                                                         |
| `rbac.enabled`                             | Enable Galaxy job RBAC. This will grant the service account the necessary permissions/roles to view jobs and pods in this namespace. Defaults to true.                                                     |
| `webHandlers.{}`                           | Configuration for the web handlers (<a href="#handlers">See table below for all options</a>)                                                                                                                                       |
| `jobHandlers.{}`                           | Configuration for the job handlers (<a href="#handlers">See table below for all options</a>)                                                                                                                                       |
| `workflowHandlers.{}`                      | Configuration for the workflow handlers (<a href="#handlers">See table below for all options</a>)                                                                                                                                  |
| `resources.limits.memory`                  | The maximum memory that can be allocated.                                                                                                                                                                  |
| `resources.requests.memory`                | The requested amount of memory.                                                                                                                                                                            |
| `resources.limits.cpu`                     | The maximum CPU that can be alloacted.                                                                                                                                                                     |
| `resources.limits.ephemeral-storage`       | The maximum ephemeral storage that can be allocated.                                                                                                                                                       |
| `resources.requests.cpu`                   | The requested amount of CPU (as time or number of cores)                                                                                                                                                   |
| `resources.requests.ephemeral-storage`     | The requested amount of ephemeral storage                                                                                                                                                                  |
| `securityContext.fsGroup`                  | The [group](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) for any files created.                                                                                             |
| `tolerations`                              | Define the `taints` that are tolerated.                                                                                                                                                                    |
| `extraFileMappings.{}`                     | Add extra files mapped as configMaps or Secrets at arbitrary paths. <a href="galaxy/values.yaml">See `values.yaml`</a> for examples.                                                                                                        |
| `extraInitCommands`                        | Extra commands that will be run during initialization.                                                                                                                                                     |
| `extraInitContainers.[]`                   | A list of extra init containers for the handler pods                                                                                                                                                       |
| `extraVolumeMounts.[]`                     | List of volumeMounts to add to all handlers                                                                                                                                                                |
| `extraVolumes.[]`                          | List of volumes to add to all handlers                                                                                                                                                                     |
| `postgresql.enabled`                       | Enable the postgresql condition in the [requirements.yml](https://github.com/galaxyproject/galaxy-helm/blob/master/galaxy/requirements.yaml).                                                              |
| `influxdb.username`                        | Influxdb user name.                                                                                                                                                                                        |
| `influxdb.url`                             | The connection URL to in the `influxdb`                                                                                                                                                                    |
| `influxdb.enabled`                         | Enable the `influxdb` used by the metrics scraper.                                                                                                                                                         |
| `influxdb.password`                        | Password for the influxdb user.                                                                                                                                                                            |
| `metrics.podAnnotations.{}`                | Dictionary of annotations to add to the metrics deployment's metadata at the pod level                                                                                                                     |
| `metrics.image.repository`                 | The location of the [galay-metrics-scraping](https://github.com/CloudVE/galaxy-docker-k8s-metrics) image to use.                                                                                           |
| `metrics.image.pullPolicy`                 | Define the [pull policy](https://kubernetes.io/docs/concepts/containers/images/#updating-images), that is, when Kubernetes will pull the image.                                                            |
| `metrics.podSpecExtra.{}`                  | Dictionary to add to the metrics deployment's pod template under `spec`                                                                                                                                    |
| `metrics.image.tag`                        | The image version to use.                                                                                                                                                                                  |
| `metrics.annotations.{}`                   | Dictionary of annotations to add to the metrics deployment's metadata at the deployment level                                                                                                              |
| `metrics.enabled`                          | Enable metrics gathering.  The influxdb setting must be specified when using this setting.                                                                                                                 |
| `nginx.conf.client_max_body_size`          | Requests larger than this size will result in a `413 Payload Too Large`.                                                                                                                                   |
| `nginx.image.tag`                          | The Nginx version to pull.                                                                                                                                                                                 |
| `nginx.image.repository`                   | Where to obtain the Nginx container.                                                                                                                                                                       |
| `nginx.image.pullPolicy`                   | When Kubernetes will [pull](https://kubernetes.io/docs/concepts/containers/images/#updating-images) the Nginx image from the repository.                                                                   |
| `nginx.galaxyStaticDir`                    | Location at which to copy Galaxy static content in the NGINX pod init container, for direct serving. Defaults to `/galaxy/server/static`                   |


# Handlers

Galaxy defines three handler types: `jobHandlers`, `webHandlers`, and
`workflowHandlers`.  All three handler types share common configuration options.

| Parameter        | Description                                                  |
| :--------------- | :----------------------------------------------------------- |
| `replicaCount`   | The number of handlers to be spawned.                        |
| `startupDelay`   | Delay in seconds for handler startup. Used to offset handlers and avoid race conditions at first startup |
| `annotations`    | Dictionary of annotations to add to this handler's metadata at the deployment level   |
| `podAnnotations` | Dictionary of annotations to add to this handler's metadata at the pod level |
| `podSpecExtra`   | Dictionary to add to this handler's pod template under `spec` |
| `startupProbe`   | Probe used to determine if a pod has started. Other probes wait for the startup probe. <a href="#probes">See table below for all probe options</a> |
| `livenessProbe`  | Probe used to determine if a pod should be restarted. <a href="#probes">See table below for all probe options</a>       |
| `readinessProbe` | Probe used to determine if the pod is ready to accept workloads. <a href="#probes">See table below for all probe options</a> |

## Probes

Kubernetes uses probes to determine the state of a pod. Pods are not considered
to have started up, and hence other probes are not run, until the startup probes
have succeeded. Pods that fail the `livenessProbe` will be restarted and work
will not be dispatched to the pod until the `readinessProbe` returns
successfully.  A pod is `ready` when all of its containers are `ready`.

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

## Extra File Mappings

The `extraFileMappings` field can be used to inject files to arbitrary paths in the `nginx` deployment, as well as any of the `job`, `web`, or `workflow` handlers.

The contents of the file can be specified directly in the `values.yml` file with the `content` attribute.

The `tpl` flag will determine whether these contents are run through the helm templating engine.

Note: when running with `tpl: true`, brackets (`{{ }}`) not meant for Helm should be escaped. One way of escaping is: `{{ '{{ mynon-helm-content}}' }}`

```yaml
extraFileMappings:
  /galaxy/server/static/welcome.html:
    applyToWeb: true
    applyToJob: false
    applyToWorkflow: false
    applyToNginx: true
    tpl: false
    content: |
      <!DOCTYPE html>
      <html>...</html>
```

**NOTE** for security reasons Helm will not load files from outside the chart so the `path` must be a relative path to location inside the chart directory.  This will change when [helm#3276](https://github.com/helm/helm/issues/3276) is resolved.  In the interim files can be loaded from external locations by:

1. Creating a symbolic link in the chart directory to the external file, or
2. using `--set-file` to specify the contents of the file. E.g:
   `helm upgrade --install galaxy cloudve/galaxy -n galaxy --set-file extraFileMappings."/galaxy/server/static/welcome\.html".content=/home/user/data/welcome.html`

## Setting parameters on the command line

Specify each parameter using the `--set key=value[,key=value]` argument to
`helm install` or `helm upgrade`. For example,

```console
helm install my-galaxy . --set persistence.size=50Gi
```

The above command sets the Galaxy persistent volume to 50GB.

Setting Galaxy configuration file values requires the key name to be escaped.
In this example, we are upgrading an existing deployment.

```console
helm upgrade my-galaxy . --set "configs.galaxy\.yml.brand"="Hello World"
```

You can also set the galaxy configuration file in its entirety with:

```console
helm install my-galaxy . --set-file "configs.galaxy\.yml"=/path/to/local/galaxy.yml
```

To unset an existing file and revert to the container's default version:

```console
helm upgrade my-galaxy . --set "configs.job_conf\.xml"=null
```

Alternatively, any number of YAML files that specifies the values of the parameters can be
provided when installing the chart. For example,

```console
helm install my-galaxy . -f values.yaml -f new-values.yaml
```

To unset a config file in a values file, use the YAML null type:

```
configs:
  job_conf.xml: ~
```

## Data persistence

By default, the Galaxy handlers store all user data under
`/galaxy/server/database/` path in each container. This path can be changed via
`persistence.mountPath` variable. Persistent Volume Claims (PVCs) are used to
share the data across deployments. It is possible to specify en existing PVC via
`persistence.existingClaim`. Alternatively, a value for
`persistence.storageClass` can be supplied to designate a desired storage class
for dynamic provisioning of the necessary PVCs. If neither value is supplied,
the default storage class for the K8s cluster will be used.

For multi-node scenarios, we recommend a storage class that supports
`ReadWriteMany`, such as the
[nfs-provisioner](https://github.com/helm/charts/tree/master/stable/nfs-server-provisioner)
as the data must be available to all nodes in the cluster.

In single-node scenarios, you must use `--set persistence.accessMode="ReadWriteOnce"`.

### Note about persistent deployments and restarts

If you wish to make your deployment persistent or restartable (bring deployment
down, keep the state in disk, then bring it up again later in time), you should
create PVCs for Galaxy and Postgres and use the `persistence.existingClaim`
variable to point to them as explained in the previous section. In addition, you
must set the `postgresql.galaxyDatabasePassword` variable; otherwise, it will be
autogenerated and will mismatch when restoring.

## Production settings

Note that this deployment mode does not work on a Mac because of an
unresolved issue in the CVMFS-CSI driver.

To install this configuration of the chart, we need to enable CVMFS deployment.
Depending on the setup of the cluster you have available, you may also need
to supply values for the cluster storage classes or PVCs.

If you wish to install a single Galaxy CVMFS-CSI and Postgres operator release
to be used by multiple Galaxy releases, you can do so by installing the CVMFS
separately as shown below:

```console
helm repo add cloudve https://raw.githubusercontent.com/CloudVE/helm-charts/master/
helm repo add zalando https://raw.githubusercontent.com/zalando/postgres-operator/master/charts/postgres-operator/
helm repo update
kubectl create namespace psql
helm install psql-operator --namespace psql zalando/postgres-operator --set persistence.enabled=true
kubectl create namespace cvmfs
helm install galaxy-cvmfs --namespace cvmfs cloudve/galaxy-cvmfs-csi --set repositories.cvmfs-gxy-data="data.galaxyproject.org"
helm install galaxy cloudve/galaxy --set cvmfs.enabled=true --set cvmfs.deploy=false
```

If you wish to get a quick deployment of a single Galaxy instance with its own
CVMFS-CSI, you can do so by enabling the CVMFS deployment as part of this chart:

```console
helm repo add cloudve https://raw.githubusercontent.com/CloudVE/helm-charts/master/
helm repo update
helm install galaxy cloudve/galaxy --set cvmfs.enabled=true --set cvmfs.deploy=true
```

If you use the latter method, it is highly recommended that you deploy a single
Galaxy release per nodepool/namespace, as multiple CVMFS-CSI provisioners and Postgres
operator running side-by-side can interfer with one another.

## Making Interactive Tools work on localhost

In general, Interactive Tools should work out of the box as long as you have a wildcard DNS mapping
to *.its.<host_name>. To make Interactive Tools work on localhost, you can use dnsmasq or similar to
handle wildcard DNS mappings for *.localhost.

For mac:
```bash
  $ brew install dnsmasq
  $ cp /usr/local/opt/dnsmasq/dnsmasq.conf.example /usr/local/etc/dnsmasq.conf
  $ edit /usr/local/etc/dnsmasq.conf and set

    address=/localhost/127.0.0.1

  $ sudo brew services start dnsmasq
  $ sudo mkdir /etc/resolver
  $ sudo touch /etc/resolver/localhost
  $ edit /etc/resolver/localhost and set

    nameserver 127.0.0.1

  $ sudo brew services restart dnsmasq
```

This should make all *.localhost and *.its.localhost map to 127.0.0.1, and ITs should work with a regular
helm install on localhost.


## Horizontal scaling

The Galaxy application can be horizontally scaled for the web, job, or workflow handlers
by setting the desired values of the `webHandlers.replicaCount`,
`jobHandlers.replicaCount`, and `workflowHandlers.replicaCount` configuration options.

## Galaxy versions

Some changes introduced in the chart sometimes rely on changes in the Galaxy
container image, especially in relation to the Kubernetes runner. This table
keeps track of recommended Chart versions for particular Galaxy versions as
breaking changes are introduced. Otherwise, the Galaxy image and chart should be
independently upgrade-able. In other words, upgrading the Galaxy image from
`21.05` to `21.09` should be a matter of `helm upgrade mygalaxy cloudve/galaxy
--reuse-values --set image.tag=21.09`.


| Chart version        | Galaxy version   | Description     |
| :------------------ | :--------------- | :-------------- |
| `4.0`               | `21.05`          | Needs [Galaxy PR#11899](https://github.com/galaxyproject/galaxy/pull/11899) for eliminating the CVMFS. If running chart 4.0+ with Galaxy image `21.01` or below, use the CVMFS instead with `--set initJob.downloadToolConfs.enabled=false --set cvmfs.repositories.cvmfs-gxy-cloud=cloud.galaxyproject.org --set cvmfs.galaxyPersistentVolumeClaims.cloud.storage=1Gi --set cvmfs.galaxyPersistentVolumeClaims.cloud.storageClassName=cvmfs-gxy-cloud --set cvmfs.galaxyPersistentVolumeClaims.cloud.mountPath=/cvmfs/cloud.galaxyproject.org` |

## Funding

- _Version 3+_: Galaxy Project, Genomics Virtual Laboratory (GVL)

- _Version 2_: Genomics Virtual Laboratory (GVL), Galaxy Project, and European
  Commission (EC) H2020 Project PhenoMeNal, grant agreement number 654241.

- _Version 1_: European Commission (EC) H2020 Project PhenoMeNal, grant
  agreement number 654241.
