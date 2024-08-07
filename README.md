# Galaxy Helm Chart (v5)

[Galaxy](https://galaxyproject.org/) is a data analysis platform focusing on
accessibility, reproducibility, and transparency of primarily bioinformatics
data. This repo contains a [Helm chart](https://helm.sh/) for easily deploying
Galaxy on top of Kubernetes. The chart allows application configuration changes,
updates, upgrades, and rollbacks.

## Supported software versions

- Kubernetes 1.27+
- Helm 3.5+

## Kubernetes cluster

You will need `kubectl` ([instructions](https://kubernetes.io/docs/tasks/tools/#kubectl))
and `Helm` ([instructions](https://helm.sh/docs/intro/install/)) installed.

### Running Galaxy locally in a dev environment

For testing and development purposes, an easy option to get Kubernetes running
is to install [Rancher Desktop](https://rancherdesktop.io/). Once you have it
installed, you will also need to setup an ingress controller. Rancher uses
*Traefik* as the default one, so disable it first by unchecking `Enable Traefik`
from the `Kubernetes Settings` page. Then deploy the NGINX ingress controller:
```
helm upgrade --install ingress-nginx ingress-nginx \
  --repo https://kubernetes.github.io/ingress-nginx \
  --namespace ingress-nginx --create-namespace
```

## Dependency charts

This chart relies on the features of other charts for common functionality:
- [postgres-operator](https://github.com/zalando/postgres-operator) for the
  database;
- [galaxy-cvmfs-csi](https://github.com/CloudVE/galaxy-cvmfs-csi-helm) for linking the
  reference data to Galaxy and jobs based on CVMFS (default).
- [csi-s3](https://github.com/ctrox/csi-s3/pull/75/) for linking
  reference data to Galaxy and jobs based on S3FS (optional/alternative to CVMFS).
- [rabbitmq-cluster-operator](https://github.com/rabbitmq/cluster-operator) for deploying
  the message queue.

In a production setting, especially if the intention is to run multiple Galaxies
in a single cluster, we recommend installing the dependency charts separately
once per cluster, and installing Galaxy with `--set postgresql.deploy=false
--set s3csi.deploy=false --set cvmfs.deploy=false --set rabbitmq.deploy=false`.

---

## Installing the chart

### Using the chart from the packaged chart repo

1. The chart is automatically packaged, versioned and uploaded to a helm repository
on each accepted PR. Therefore, the latest version of the chart can be downloaded
from this repository.

```console
helm repo add cloudve https://raw.githubusercontent.com/CloudVE/helm-charts/master/
helm repo update
```

2. Install the chart with the release name `my-galaxy`. It is not advisable to
   install Galaxy in the `default` namespace.

```console
helm install my-galaxy-release cloudve/galaxy
```

### Using the chart from GitHub repo

1. Clone this repository and add required dependency charts:

```console
git clone https://github.com/galaxyproject/galaxy-helm.git
cd galaxy-helm/galaxy
helm dependency update
```

2. To install the chart with the release name `my-galaxy`. See [Data
   persistence](#data-persistence) section below about the use of persistence
   flag that is suitable for your Kubernetes environment.

```console
helm install --create-namespace -n galaxy my-galaxy . --set persistence.accessMode="ReadWriteOnce"
```

In several minute, Galaxy will be available at `/galaxy/` URL of your Kubernetes
cluster. If you are running the development Kubernetes, Galaxy will be available
at `http://localhost/galaxy/` (note the trailing slash).

## Uninstalling the chart

To uninstall/delete the `my-galaxy` deployment, run:

```console
helm delete my-galaxy
```

if you see that some RabbitMQ and Postgres elements remain after some 10 minutes or more, you should be able to issue:

```
kubectl delete RabbitmqCluster/my-galaxy-rabbitmq-server
kubectl delete statefulset/galaxy-my-galaxy-postgres
```

it might be needed to remove the finalizer from the RabbitmqCluster if the above doesn't seem to get rid of RabbitmqCluster, through a

```
kubectl edit RabbitmqCluster/my-galaxy-rabbitmq-server
```

remove the finalizer in:

```
apiVersion: rabbitmq.com/v1beta1
kind: RabbitmqCluster
metadata:
  annotations:
    meta.helm.sh/release-name: my-galaxy
    meta.helm.sh/release-namespace: default
  creationTimestamp: "2022-12-19T16:54:33Z"
  deletionGracePeriodSeconds: 0
  deletionTimestamp: "2022-12-19T17:41:40Z"
  finalizers:
  - deletion.finalizers.rabbitmqclusters.rabbitmq.com
```

and remove the postgres secret:

```
kubectl delete secrets/standby.galaxy-my-galaxy-postgres.credentials.postgresql.acid.zalan.do
```

Consider as well that if you set persistence to be enabled, Postgres and Galaxy will leave their PVCs behind, which you might want to delete or not depending on your use case.

## Configuration

The following table lists the configurable parameters of the Galaxy chart. The
current default values can be found in `values.yaml` file.

| Parameters                                 | Description                                                                                                                                                                                                |
|--------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `nameOverride`                             | Override the name of the chart used to prefix resource names. Defaults to `{{.Chart.Name}}` (e.g., `galaxy`)                                                                                                |
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
| `jobs.rules`                               | Galaxy dynamic job rules. See <a href="galaxy/values.yaml">`values.yaml`</a>                                                                                                                                                                |
| `jobs.priorityClass.existingClass`         | Use an existing [priorityClass](https://kubernetes.io/docs/concepts/configuration/pod-priority-preemption/#priorityclass) to assign if `jobs.priorityClass.enabled=true`                                   |
| `refdata.enabled`                          | Whether or not to mount cloud-hosted Galaxy reference data and tools.                                           |
| `refdata.type`                             | `s3csi` or `cvmfs`, determines the CSI to use for mounting reference data. `cvmfs` is the default type for reference data. |
| `s3csi.deploy`                             | Deploy the CSI-S3 Helm Chart. This is an optional dependency, and for production scenarios it should be deployed separately as a cluster-wide resource.          |
| `cvmfs.deploy`                             | Deploy the Galaxy-CVMFS-CSI Helm Chart. This is an optional dependency, and for production scenarios it should be deployed separately as a cluster-wide resource                                           |
| `cvmfs.enabled`                            | Enable use of CVMFS in configs, and deployment of CVMFS Persistent Volume Claims for Galaxy                                                                                                                |
| `cvmfs.pvc.{}`                             | Persistent Volume Claim to deploy for CVMFS repositories. See <a href="galaxy/values.yaml">`values.yaml`</a> for examples.                                                                                                                 |
| `setupJob.ttlSecondsAfterFinished`          | Sets `ttlSecondsAfterFinished` for the initialization jobs. See the [Kubernetes documentation](https://kubernetes.io/docs/concepts/workloads/controllers/ttlafterfinished/#ttl-controller) for more details.       |
| `setupJob.downloadToolConfs.enabled`        | Download configuration files and the `tools` directory from an archive via a job at startup                                                                                                                |
| `setupJob.downloadToolConfs.archives.startup` | A URL to a `tar.gz` publicly accessible archive containing AT LEAST conf files and XML tool wrappers. Meant to be enough for Galaxy handlers to startup.                                                   |
| `setupJob.downloadToolConfs.archives.running` | A URL to a `tar.gz` publicly accessible archive containing AT LEAST confs, tool wrappers, and tool scripts but excluding test data. Meant to be enough for Galaxy handlers to run jobs.                    |
| `setupJob.downloadToolConfs.archives.full`  | A URL to a `tar.gz` publicly accessible archive containing the full `tools` directory, including each tool's test data. Meant to be enough to run automated tool-tests, fully mimicking CVMFS repositories |
| `setupJob.downloadToolConfs.volume.mountPath` | Path at which to mount the unarchived confs in the each handler (should match path set in the tool confs)                                                                                                  |
| `setupJob.downloadToolConfs.volume.subPath` | Name of subdirectory on Galaxy's shared filesystem to use for the unarchived configs                                                                                                                       |
| `setupJob.createDatabase`                   | Deploy a job to create a Galaxy database from scratch (does not affect subsequent upgrades, only first startup)                                                                                            |
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
| `extraFileMappings.{}`                     | Add extra files mapped as configMaps or Secrets at arbitrary paths. See <a href="galaxy/values.yaml">`values.yaml`</a> for examples.                                                                                                        |
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

# Additional Configurations

## Extra File Mappings

The `extraFileMappings` field can be used to inject files to arbitrary paths in the `nginx` deployment, as well as any of the `job`, `web`, or `workflow` handlers, and the `init` jobs.

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
    applyToSetupJob: false
    tpl: false
    content: |
      <!DOCTYPE html>
      <html>...</html>
```

**NOTE** for security reasons Helm will not load files from outside the chart so the `path` must be a relative path to location inside the chart directory.  This will change when [helm#3276](https://github.com/helm/helm/issues/3276) is resolved.  In the interim files can be loaded from external locations by:

1. Creating a symbolic link in the chart directory to the external file, or
2. using `--set-file` to specify the contents of the file. E.g:
   `helm upgrade --install galaxy cloudve/galaxy -n galaxy --set-file extraFileMappings."/galaxy/server/static/welcome\.html".content=/home/user/data/welcome.html --set extraFileMappings."/galaxy/server/static/welcome\.html".applyToWeb=true`
   
Alternatively, if too many `.applyTo` need to be set, the apply flags can be inserted instead to the `extraFileMappings` (in addition to the --set-file in the cli) for that file in your `values.yaml`, with no `content:` part (as that is done through the `--set-file`):

```
extraFileMappings:
  /galaxy/server/static/welcome.html:
    applyToJob: false
    applyToWeb: true
    applyToSetupJob: false
    applyToWorkflow: false
    applyToNginx: false
    tpl: false
```

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
persist the data across deployments. It is possible to specify en existing PVC via
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

## Making Interactive Tools work on localhost

In general, Interactive Tools should work out of the box as long as you have a
wildcard DNS mapping to `*.its.<host_name>`. To make Interactive Tools work on
localhost, you can use `dnsmasq` or similar to handle wildcard DNS mappings for
`*.localhost`.

For linux:
Follow the instructions here to configure dnsmasq on Linux: https://superuser.com/a/1718296

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

This should make all *.localhost and *.its.localhost map to 127.0.0.1, and ITs
should work with a regular helm install on localhost.

## Horizontal scaling

The Galaxy application can be horizontally scaled for the web, job, or workflow handlers
by setting the desired values of the `webHandlers.replicaCount`,
`jobHandlers.replicaCount`, and `workflowHandlers.replicaCount` configuration options.

## Cron jobs

Two Cron jobs are defined by default.  One to clean up Galaxy's database and one to clean up the `tmp` directory.  By default, these
jobs run at 02:05 (the database maintenance script) and 02:15 (`tmp` directyory cleanup). Users can 
change the times the cron jobs are run by changing the `schedule` field in the `values.yaml` file:

```yaml
cronJobs:
  maintenance:
    schedule: "30 6 * * *" # Execute the cron job at 6:30 UTC
```
or by specifying the `schedule` on the command line when instaling Galaxy:
```bash
# Schedule the maintenance job to run at 06:30 on the first day of each month
helm install galaxy -n galaxy galaxy/galaxy --set cronJobs.maintenance.schedule="30 6 1 * *"
```
To disable a cron job after Galaxy has been deployed simply set the enabled flag for that job to false:


```bash
helm upgrade galaxy -n galaxy galaxy/galaxy --reuse-values --set cronJobs.maintenance.enabled=false
```

### Run a CronJob manually

Cron jobs can be invoked manually with tools such as [OpenLens](https://github.com/MuhammedKalkan/OpenLens)
or from the command line with `kubectl`
```bash
kubectl create job --namespace <namespace> <job name> --from cronjob/galaxy-cron-maintenance 
```
This will run the cron job regardless of the `schedule` that has been set.

**Note:** the name of the cron job will be `{{ .Release.Name }}-cron-<job name>` where the `<job name>`
is the name (key) used in the `values.yaml` file.

### CronJob configuration

The following fields can be specified when defining cron jobs.

| Name | Definition                                                                                                                                | Required |
|---|-------------------------------------------------------------------------------------------------------------------------------------------|----------|
| enabled | `true` or `false`.  If `false` the cron job will not be run.  Default is `true` | **Yes**  |
| schedule | When the job will be run.  Use tools such as [crontab.guru](https://crontab.guru) for assistance determining the proper schedule string   | **Yes**  |
| defaultEnv | `true` or `false`. See the `galaxy.podEnvVars` macro in `_helpers.tpl` for the list of variables that will be defined. Default is `false` | No       |
| extraEnv | Define extra environment variables that will be available to the job | No       |
| securityContext | Specifies a `securityContext` for the job. Typically used to set `runAsUser` | No       |
| image | Specify the Docker container used to run the job | No       |
| command | The command to run | **Yes**  |
| args | Any command line arguments that should be passed to the `command` | No       |
| extraFileMappings | Allow arbitrary files to be mounted from config maps | No       |

### Notes

If specifying the Docker `image` both the `resposity` and `tag` MUST be specified.
```yaml
  image:
    repository: quay.io/my-organization/my-image
    tag: "1.0"  
```

The `extraFileMappings` block is similar to the global `extraFileMappings` except the file will only be mounted for that cron job.
The following fields can be specified for each file.

| Name | Definition | Required |
|---|---|----------|
| mode | The file mode (permissions) assigned to the file | No       |
| tpl | If set to `true` the file contents will be run through Helm's templating engine. Defaults to `false` | No       |
| content | The contents of the file | **Yes**  | 


See the `example` cron job included in the `values.yaml` file for a full example.


