# Configuration

The following table lists the configurable parameters of the Galaxy chart. The
current default values can be found in `values.yaml` file.

| Parameters                           | Description                                                                                                                                  |
|--------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| `nameOverride`                       | Override the name of the chart used to prefix resource names. Defaults to `{{.Chart.Name}}` (i.e. `galaxy`)                                  |
| `fullnameOverride`                   |                                                                                                                                              |
| `image.repository`                   | The repository and name of the Docker image for Galaxy, searches Docker Hub by default                                                       |
| `image.tag`                          | Galaxy Docker image tag (generally corresponds to the desired Galaxy version)                                                                |
| `image.pullPolicy`                   | Galaxy image [pull policy](https://kubernetes.io/docs/concepts/configuration/overview/#container-images) for more info                       |
| `service.type`                       | Kubernetes [Service type](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types)                |
| `service.port`                       | Kubernetes service port                                                                                                                      |
| `service.nodePort`                   | If `service.type` is set to `NodePort`, then this can be used to set the port at which Galaxy will be available on all nodes' IP addresses   |
| `workflowHandlers.*`                 |                                                                                                                                              |
| `webHandlers.*`                      |                                                                                                                                              |
| `jobHandlers.*`                      |                                                                                                                                              |
| `metrics.enabled`                    |                                                                                                                                              |
| `metrics.image.repository`           |                                                                                                                                              |
| `metrics.image.tag`                  |                                                                                                                                              |
| `metrics.image.pullPolicy`           |                                                                                                                                              |
| `rbac.enabled`                       | Enable Galaxy job RBAC                                                                                                                       |
| `rbac.serviceAccount`                |                                                                                                                                              |
| `securityContext.fsGroup`            |                                                                                                                                              |
| `persistence.enabled`                | Enable persistence using PVC                                                                                                                 |
| `persistence.name`                   | Name of the PVC                                                                                                                              |
| `persistence.accessMode`             | PVC access mode for the Galaxy volume                                                                                                        |
| `persistence.size`                   | PVC storage request for the Galaxy volume, in GB                                                                                             |
| `persistence.mountPath`              | Path where to mount the Galaxy volume                                                                                                        |
| `extraInitCommands`                  |                                                                                                                                              |
| `extraEnv`                           |                                                                                                                                              |
| `ingress.enabled`                    | Enable Kubernetes ingress                                                                                                                    |
| `ingress.canary.enabled`             |                                                                                                                                              |
| `ingress.annotations.*`              |                                                                                                                                              |
| `ingress.path`                       | Path where Galaxy application will be hosted                                                                                                 |
| `ingress.hosts`                      |                                                                                                                                              |
| `ingress.tls`                        |                                                                                                                                              |
| `resources.requests.cpu`             |                                                                                                                                              |
| `resources.requests.memory`          |                                                                                                                                              |
| `resources.requests.ephemeral-storage` |                                                                                                                                              |
| `resources.limits.cpu`               |                                                                                                                                              |
| `resources.limits.memory`            |                                                                                                                                              |
| `resources.limits.ephemeral-storage` |                                                                                                                                              |
| `tolerations`                        |                                                                                                                                              |
| `postgresql.enabled`                 |                                                                                                                                              |
| `cvmfs.enabled`                      |                                                                                                                                              |
| `cvmfs.deploy`                       |                                                                                                                                              |
| `useSecretConfigs`                   | Enable Kubernetes Secrets for all config maps                                                                                                |
| `configs.*`                          | Galaxy configuration files and values for each of the files. The provided value represent the entire content of the given configuration file |
| `jobs.rules`                         | Galaxy dynamic job rules                                                                                                                     |
| `extraFileMappings.*`                |                                                                                                                                              |
| `influxdb.enabled`                   |                                                                                                                                              |
| `influxdb.url`                       |                                                                                                                                              |
| `influxdb.username`                  |                                                                                                                                              |
| `influxdb.password`                  |                                                                                                                                              |
| `nginx.image.repository`             |                                                                                                                                              |
| `nginx.image.tag`                    |                                                                                                                                              |
| `nginx.image.pullPolicy`             |                                                                                                                                              |
| `nginx.conf.client_max_body_size`    |                                                                                                                                              |
| `jobHandlers.priorityClass.enabled`                |                                                              |
| `jobHandlers.priorityClass.existingClass`          |                                                              |
# Handlers

Each of the handlers [`workflowHandlers`, `webHandlers`, and `jobHandler`] share common configurations for `replicaCount`, `priorityClass`, and readiness and liveness probes.

| Parameters | Description |
|------|-----|
| `replicaCount`                    | The number of workflowHandlers to be spawned |
| priorityClass.enabled |  |
| priorityClass.existingClass |  |

# Readiness and Liveness Probes

Each of the handler may have readiness and liveness probes defined.

| Probes |
|-----|
| jobHandlers.readinessProbe|
| jobHandlers.livenessProbe| |
| webHandlers.readinessProbe| |
| webHandlers.livenessProbe| |
| workflowHandlers.readinessProbe| |
| workflowHandlers.livenessProbe| |




| Parameters | Description |
|-----|-----|
| `enabled`          | Set to true to enable the probe. A pod is *ready* when all of the containers in the pod are ready. Handlers that do not respond to the liveness probe will be restarted by Kubernetes. |
| `periodSeconds`    | How frequently Kubernetes with probe the handler. |
| `failureThreshold` | The number of times Kubernetes will retry the probe before giving up. |
| `timeoutSeconds`   | How long Kubernetes will wait for a probe to timeout. |


