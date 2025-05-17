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
