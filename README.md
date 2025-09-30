# Galaxy Helm Chart (v6)

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
- [postgres-operator](https://cloudnative-pg.io/documentation/current/) for the
  database;
- [galaxy-cvmfs-csi](https://github.com/CloudVE/galaxy-cvmfs-csi-helm) for linking the
  reference data to Galaxy and jobs based on CVMFS (default).
- [csi-s3](https://github.com/yandex-cloud/k8s-csi-s3/tree/master/deploy/helm/csi-s3) for linking
  reference data to Galaxy and jobs based on S3FS (optional/alternative to CVMFS).
- [rabbitmq-cluster-operator](https://github.com/rabbitmq/cluster-operator) for deploying
  the message queue.

In a production setting, especially if the intention is to run multiple Galaxies
in a single cluster, we recommend installing the dependency charts separately
once per cluster. For convenience, we provide a `galaxy-deps` helm chart that will
install all of these general dependencies (often installable cluster-wide) for you.
Simply install using
`helm install --create-namespace -n galaxy-deps galaxy-deps galaxyproject/galaxy-deps`.

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

2. Install global dependencies such as the postgres operator.

```console
helm install --create-namespace -n galaxy-deps galaxy-deps cloudve/galaxy-deps
```

3. Install the chart with the release name `my-galaxy`. It is not advisable to
   install Galaxy in the `default` namespace.

```console
helm install -n my-namespace my-galaxy-release cloudve/galaxy
```

### Using the chart from GitHub repo

1. Clone this repository:

```console
git clone https://github.com/galaxyproject/galaxy-helm.git
```

2. Setup cluster-wide operators and dependencies:

```console
cd galaxy-helm/galaxy-deps
helm dependency update
helm install --create-namespace -n galaxy-deps galaxy-deps .
```

3. To install the chart with the release name `my-galaxy`. See [Data
   persistence](#data-persistence) section below about the use of persistence
   flag that is suitable for your Kubernetes environment.

```console
cd ../galaxy
helm dependency update
helm install --create-namespace -n galaxy my-galaxy . --set persistence.accessMode="ReadWriteOnce"
```

In several minute, Galaxy will be available at `/galaxy/` URL of your Kubernetes
cluster. If you are running the development Kubernetes, Galaxy will be available
at `http://localhost/galaxy/` (note the trailing slash).

## Uninstalling the chart

To uninstall/delete the `my-galaxy` deployment, run:

```console
helm delete my-galaxy -n galaxy
```

If you no longer require cluster-wide operators, you can optionally uninstall them, although,
in general, we recommend installing them once and leaving them as is.

```console
helm delete -n galaxy-deps galaxy-deps
```

## Configuration

The following table lists the configurable parameters of the Galaxy chart. The
current default values can be found in `values.yaml` file.

| Key | Description |
|-----|-------------|
| nameOverride | Partial override of the `galaxy.fullname`.  The `.Release.Name` will be prepended to generate the fullname. |
| fullnameOverride | Fully override the `galaxy.fullname` |
| image.repository | Repository containing the Galaxy image. |
| image.tag | Galaxy Docker image tag (generally corresponds to the desired Galaxy version) |
| image.pullPolicy | Galaxy image [pull policy](https://kubernetes.io/docs/concepts/configuration/overview/#container-images) |
| imagePullSecrets | Secrets used to [access a Galaxy image from a private repository](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/) |
| reuseExistingDirectory | Configure the CNPG operator to reuse an existing PGDATA directory if it exists, otherwise the operator will rename the existing directory. |
| trainingHook | Configure the GTN webhook |
| trainingHook.enabled | Enable the GTN webhook to link references to tools in tutorials to the corresponding tool panel in Galaxy. |
| trainingHook.url | The training material server used to service the training-material webhook. |
| service.type | The Galaxy service type |
| service.port | The port Galaxy is listening to |
| service.nodePort | The external port exposed on each node |
| metrics.enabled | Enable the metrics server. Defaults to `false` |
| serviceAccount.create | Specifies whether a service account should be created |
| serviceAccount.annotations | Annotations to add to the service account |
| serviceAccount.name | The name of the service account to use. If not set and create is true, a name is generated using the fullname template |
| rbac.enabled | Does the cluster use role based access control. |
| securityContext.runAsUser | UID of the system user used by jobs. This user must exist in the container. |
| securityContext.runAsGroup | GID of the system group used by jobs. This group must exist in the container. |
| securityContext.fsGroup | Security context and file system group used by jobs. |
| persistence | Configure the PVC used by Galaxy for local storage. |
| persistence.enabled | Persistence is enabled by default |
| persistence.name | Name of the PVC to create |
| persistence.storageClass | StorageClass for the PVC. Must support `ReadWriteMany`. |
| persistence.existingClaim | The name of an existing PVC to use for persistence. |
| setupJob | tasks to perform once after installation |
| setupJob.createDatabase | create the database |
| setupJob.downloadToolConfs.archives.startup | A tar.gz publicly accessible archive containing AT LEAST conf files and XML tool wrappers. Meant to be enough for Galaxy handlers to startup |
| setupJob.downloadToolConfs.archives.running | A tar.gz publicly accessible archive containing AT LEAST confs, tool wrappers, and scripts excluding test data. Meant to be enough for Galaxy handlers to run jobs. |
| setupJob.downloadToolConfs.archives.full | A tar.gz publicly accessible archive containing the full `tools` directory, including each tool's test data. Meant to be enough to run automated tool-tests, fully mimicking CVMFS setup |
| extraInitContainers | Allow users to specify extra init containers |
| cronJobs | CronJobs to perform periodic maintenance tasks |
| cronJobs.maintenance | Runs the maintenance.sh script to purge items in the Galaxy database that have been flagged as deleted. |
| cronJobs.maintenance.extraSettings.days | Purge items older than this. |
| cronJobs.tmpdir | Remove files from the tmp directory that are older than the allowable wall time for a job |
| ingress.enabled | Should ingress be enabled. Defaults to `true` |
| resources.requests | We recommend updating these based on the usage levels of the server. |
| postgresql.existingDatabase | hostname and port of an existing database to use. |
| refdata | Configuration block for reference data |
| refdata.enabled | Whether or not to mount cloud-hosted Galaxy reference data and tools. |
| refdata.type | `s3csi` or `cvmfs`, determines the CSI to use for mounting reference data. `cvmfs` is the default and recommended for the time being. |
| cvmfs | Configuration block if `cvmfs` is used as `refdata.type` |
| cvmfs.deploy | Deploy the Galaxy-CVMFS-CSI Helm Chart. This is an optional dependency, and for production scenarios it should be deployed separately as a cluster-wide resource |
| s3csi | Configuration block if `s3csi` is used as the `refdata.type` |
| useSecretConfigs | When this flag is set to true, all configs will be set in secrets, when it is set to false, all configs will be set in configmaps |
| configs | All config files will be relative to `/galaxy/server/config/` directory |
| configs.galaxy\.yml | Galaxy configuration. See the [Galaxy documentation](https://docs.galaxyproject.org/en/master/admin/config.html) for more information. |
| jobs | Additional dynamic rules to map into the container. |
| jobs.init.image | The Docker image to use for the init containers |
| jobs.priorityClass.enabled | Assign a [priorityClass](https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/#priorityclass) to the dispatched jobs. |

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

For Debian and Ubuntu:
```bash
  $ sudo apt update
  $ sudo apt install -y dnsmasq
  $ sudo cp /etc/dnsmasq.conf /etc/dnsmasq.conf.backup
  $ sudo sh -c 'echo "address=/localhost/127.0.0.1" >> /etc/dnsmasq.conf'
  $ sudo systemctl start dnsmasq
  $ sudo systemctl enable dnsmasq
  $ sudo mkdir -p /etc/resolver
  $ sudo sh -c 'echo "nameserver 127.0.0.1" > /etc/resolver/localhost'
  $ sudo systemctl restart dnsmasq
```

For RHEL, Fedora, and Rocky Linux:
```bash
  $ sudo dnf install dnsmasq -y
  $ sudo cp /etc/dnsmasq.conf /etc/dnsmasq.conf.backup
  $ sudo sh -c 'echo "address=/localhost/127.0.0.1" >> /etc/dnsmasq.conf'
  $ sudo systemctl start dnsmasq
  $ sudo systemctl enable dnsmasq
  $ sudo mkdir -p /etc/resolver
  $ sudo sh -c 'echo "nameserver 127.0.0.1" > /etc/resolver/localhost'
  $ sudo systemctl restart dnsmasq
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


## Upgrading

## From v5 to v6

### Breaking changes

* v6 replaces the [Zalando Postgres
  operator](https://github.com/zalando/postgres-operator) with
  [CloudNativePG](https://cloudnative-pg.io/) operator for Postgres. This
  decision was made because CloudNativePG is meant to become a
  [CNCF](https://www.cncf.io/) project, has increasing popularity, and the
  avoidance of StatefulSets makes management easier. However, there is no direct
  upgrade path from Zalando to CloudNativePG. Therefore, **simply upgrading the
  Galaxy Helm chart could result in your existing database being deleted and
  possible data loss**.

  We recommend first creating a [logical
  backup](https://github.com/zalando/postgres-operator/blob/master/docs/administrator.md#logical-backups)
  of the existing Galaxy database, and then reimporting that backup to the new
  database following instructions
  [here](https://cloudnative-pg.io/documentation/1.16/database_import/).

  You can also choose not to upgrade the Postgres operator and continue using
  your existing database service. In this case, set `postgresql.enabled: false`
  in the `values.yaml` file and configure the `galaxy.yml` file to point to your
  existing database.

* v6 chart also changes the default uid of the system Galaxy user. Previously
  this uid was 101, which is a system reserved uid and can cause conflicts with system installed packages. Starting
  with v6, the default uid is 10001. This value needs to be matched between the
  container and the chart, and during this transition period, there is a
  dedicated galaxy-min image that uses the new uid. This image is available at
  `quay.io/galaxyproject/galaxy-min:24.2-uid`, and it is set as the default in
  the values file.

  As a result of this change, when upgrading from a previous version, it is
  necessary to also update the file system permissions to match the new uid.
  This can be done by running the following commands:

  ```bash
  kubectl apply -n galaxy -f https://gist.githubusercontent.com/afgane/f82703727c6ca22a695f4eb022fdccd6/raw/3ec72508f15fdaf2ac3af3eac54f05ae7cd1a164/galaxy-debug-pod.yml
  kubectl exec -n galaxy -it gxy-debug-pod -- sh
  cd /server/galaxy/database/
  find . -user 101 -exec chown 10001:10001 {} +
  ```

* v6 splits all global dependencies, such as the Postgres and RabbitMQ
  operators, into a separate `galaxy-deps` chart. This is in contrast to v5,
  which had all dependencies bundled with the Galaxy chart. This bundling caused
  problems during uninstallation in particular, because the Postgres operator
  could be uninstalled before Postgres itself was uninstalled, leaving various
  artifacts behind. This made reinstallation particularly tricky, as all such
  left-over resources had to be cleaned up manually. Chart installation notes
  already contained a recommendation that these dependencies be installed
  separately. v6 makes this separation explicit by specifically separating the
  dependencies into a separate chart.

  If upgrading in production scenarios, you may simply omit installing the
  `galaxy-deps` chart and continue as usual. If upgrading in development
  scenarios, there is no straightforward upgrade path. The Galaxy chart will
  have to be uninstalled, the `galaxy-deps` chart installed, and subsequently,
  Galaxy can be reinstalled.
