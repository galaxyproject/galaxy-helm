# TL;DR

To run a vanilla docker-galaxy-stable setup on Kubernetes using this chart on **minikube**:

```
helm install -f example_configs/galaxy-stable-18.01-minikube.yaml galaxy-helm-repo/galaxy-stable
```

This assumes that you at least followed the [First time installation](README.md#first-time-installation) part and that you have checked out this repo (where the config file is available). Please note that this setup won't send jobs to the Kubernetes cluster, as it is not configured like that on the stock docker-galaxy-stable compose galaxy images. This feature requires changes in the `config/job_conf.xml`, which would mean that you need your own `galaxy-init` container flavour (like the [one built for PhenoMeNal](https://github.com/phnmnl/container-galaxy-k8s-runtime/blob/develop/Dockerfile_init) for instance).



# Using docker-galaxy-stable compose images

Using the docker-stable compose images with Kubernetes on this setup requires building those images with certain options being passed to the images, as done [here](https://github.com/phnmnl/container-galaxy-k8s-runtime/blob/develop/simplified_galaxy_stable_container_creation.sh). Please note that you will want to have your own version of `Docker_init` (like the one [here](https://github.com/phnmnl/container-galaxy-k8s-runtime/blob/develop/Dockerfile_init)), where you can setup your flavouring, tools and other settings to personalize the Galaxy instance that you will be deploying.

## Variables

| Parameter | Description | Default |
| -------- | ----------- | ---- |
| `export_dir` | Export directory for Galaxy compose | `/export` |
| `galaxy_conf.brand` | Branding text displayed on Galaxy | `k8s` |
| `init.image.repository` | Repository for the docker image: `<server>/<owner>/<image-name>` for Galaxy init. | `pcm32/galaxy-stable-k8s-init` |
| `init.image.tag` | Image tag for Galaxy init image. | `pcm32/galaxy-stable-k8s` |
| `init.image.pullPolicy` | Pull policy for the Galaxy init image | `IfNotPresent` |
| `init.resources` | k8s resources map for the init process | |
| `image.repository` | Repository for the docker image: `<server>/<owner>/<image-name>` for Galaxy main process. | `pcm32/galaxy-stable-k8s` |
| `image.tag` | Image tag for Galaxy image. | `latest` |
| `image.pullPolicy` | Pull policy for the Galaxy image. | `IfNotPresent` |
| `tools.destination` | Directory where tools are stored, possibly not needed and should be removed. | `/export/tools` |
| `k8s.supp_groups` | Kubernetes supplemental group (this is probably a list), used for writing with adequate privileges to certain shared file systems | |
| `k8s.fs_group` | Kubernetes file system group (this is probably a list), used for writing with adequate privileges to certain shared file systems | |
| `admin.email` | Admin email to setup Galaxy with. | |
| `admin.password` | Admin password to setup Galaxy with. | |
| `admin.api_key` | Admin api_key to setup Galaxy with. | |
| `admin.username` | Admin username to setup Galaxy with. | |
| `admin.allow_user_creation` | Configures `allow_user_creation` Galaxy config environment variable. | `"True"` |
| `galaxy_conf.smtp_server` | SMTP server for Galaxy password reset functionality ||
| `galaxy_conf.smtp_username` | SMTP username for Galaxy password reset functionality ||
| `galaxy_conf.smtp_password` | SMTP password for Galaxy password reset functionality ||
| `galaxy_conf.email_from` | SMTP email_from for Galaxy password reset functionality ||
| `galaxy_conf.smtp_ssl` | SMTP ssl for Galaxy password reset functionality ||
| `galaxy_conf.url` | Incoming URL label for Galaxy password reset functionality, shown on reset email to identify instance. ||
| `galaxy_conf.allow_user_deletion` | Allows the admin to delete users | |
| `galaxy_conf.allow_user_creation` | Allows the admin to delete users | |
| `galaxy_conf.containers_resolvers_config_file` | Config file path for resolving containers | `"/export/config/container_resolvers_conf.xml"` |
| `galaxy_conf.ftp_upload_site` | Incoming URL for sftp uploads. ||
| `service.port` | Internal port where the Galaxy container serves content. | `80` |
| `service.nodePortExposed` | Internal port where the Galaxy container serves content. | `30700` |
| `service.name` | Name to use for the k8s service exposing Galaxy | `galaxy-svc` |
| `service.type` | Type of k8s service for Galaxy | `ClusterIP` |
| `persistence.enabled` | Whether to create or not a PVC for Galaxy, defaults to true. | `true` |
| `persistence.name` | Name for the PVC that Galaxy and scheduled jobs will use. | `galaxy-pvc` |
| `persistence.size` | Amount of this that the PVC requests, such as "15Gi" | `15Gi` |
| `persistence.subPath` | Subpath within the PV where the PVC should reside. | |
| `persistence.minikube.enabled` | Whether to create a Persistent Volume in minikube or not. | `true` |
| `persistence.minikube.hostPath` | Path in the minikube VM for galaxy data directory (where PV gets created). |  |
| `ingress.self_managed` | Whether to use an external ingress controller or the chart's provided one, when using ingresses. | `false` |
| `ingress.enabled` | Whether to enable ingress or not... seems redundant, should be fixed. | `false` |
| `ingress.hosts` | Hostname array to construct ingress URLs to respond to (hostname.domain). | `galaxy` |
| `ingress.domain` | Domain to construct ingress URL to respond to (hostname.domain). | `local` |
| `ingress.path` | URL path for Galaxy |  |
| `ingress.annotations` | | |
| `ingress.tls` | | |
| `resources` | Resources requests and limits (k8s) for the Galaxy container when running. | |
| `postgresql.enabled` | Whether Galaxy should use postgres or not. | `true` |
| `postgresql.postgresPassword` | Password to use for postgres setup | `change_me` |
| `postgresql.postgresUser` | User for postgresql |  |
| `postgresql.postgresDatabase` | Name for the galaxy database |  |
| `postgresql.persistence.existingClaim` | Name of the Persistent Volume Claim to use with postgres, by default the same as Galaxy | `galaxy-pvc` |
| `postgresql.persistence.subPath` | A subpath in the PV where the postgres mount will be done | |
| `postgresql.fullname` | ?? | |
| `legacy.pre_k8s_16` | Whether we are running on a Kubernetes setup below 1.6 | `false` |
| `rbac.enabled` | Whether RBAC setups for the chart should be activated. | `false` |
| `condor.enabled` | Use condor or not | `false` |
| `proftpd.enabled` | Use proftpd or not | `true` |
| `proftpd.replicaCount` | Number of instances for proftpd. It is not clear whether >1 would work due to keys generation. | `1` |
| `proftpd.image.repository` | docker image for proftpd | |
| `proftpd.image.tag` | tag for the proftpd image set above | |
| `proftpd.passive_port.low` | Passive port minimum for proftpd | |
| `proftpd.passive_port.high` | Passive port maximum for proftpd | |
| `proftpd.use_sftp` | If set to true, use sftp instead of ftp | `"true"` |
| `proftpd.service.name` | Name to be given for the proftpd k8s service | |
| `proftpd.service.type` | Type of service for proftpd | `ClusterIP` |
| `proftpd.service.nodePortExposed` | Port opened on k8s nodes for exposing proftpd, when using service type `NodePort` | `30722` |
| `proftpd.generate_ssh_key` |  Whether to generate the ssh key for sftp access | "`false`" |






## Simplest setup

The minimal requirement to be able to use the docker-galaxy-stable is changing one of the compose image to install some Kubernetes software requirements. An image containing this is available on docker hub at `pcm32/galaxy-web:k8s`. This image was created through:

```
$ git clone https://github.com/bgruening/docker-galaxy-stable
$ cd docker-galaxy-stable/compose/galaxy-web
$ docker build --build-arg GALAXY_ANSIBLE_TAGS=supervisor,startup,scripts,nginx,k8 -t pcm32/galaxy-web:k8s .
```

Provided that the tools have mappings to docker containers via normal Galaxy mechanisms, after checking out this repo, running (in a machine configured to communicate with a Kubernetes cluster running helm):

```
helm install -f example_configs/simple-config-galaxy-stable.yaml galaxy-helm-repo/galaxy-stable
```

Please note the use of **galaxy-stable** at the end of the call, instead of **galaxy**. In time the **galaxy** chart used in previous examples will be deprecated in favour of **galaxy-stable**.

This will generate a galaxy instance available on any of the IPs of the Kubernetes clusters on port `30700`.

## With your own galaxy-ini image

Most probably you have a set of tools that you want to use, which means that you might need (or already have) your own flavour of the [compose/galaxy-ini](https://github.com/bgruening/docker-galaxy-stable/tree/master/compose/galaxy-init) image.

If you don't have such init container, you could build yours like it is done [here]().




## Running PhenoMeNal using the compose images

Since the PhenoMeNal Galaxy instance was the precursor in the use of Galaxy within Kubernetes, this example has been tested more.

```
helm install -f example_configs/simple-config-stable-phenomenal.yaml galaxy-helm-repo/galaxy-stable
```

This will generate a galaxy instance available on any of the IPs of the Kubernetes clusters on port `30700`.
