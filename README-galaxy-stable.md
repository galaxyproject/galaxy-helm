# TL;DR

To run a vanilla docker-galaxy-stable setup on Kubernetes using this chart on **minikube**:

```
helm install -f example_configs/galaxy-stable-18.01-minikube.yaml galaxy-helm-repo/galaxy-stable
```

This assumes that you at least followed the [Helm for the first time](README.md#galaxy-helm-charts) part and that you have checked out this repo (where the config file is available). Please note that this setup won't send jobs to the Kubernetes cluster, as it is not configured like that on the stock docker-galaxy-stable compose galaxy images. This feature requires changes in the `config/job_conf.xml`, which would mean that you need your own `galaxy-init` container flavour (like the [one built for PhenoMeNal](https://github.com/phnmnl/container-galaxy-k8s-runtime/blob/develop/Dockerfile_init) for instance).



# Using docker-galaxy-stable compose images

Using the docker-stable compose images with Kubernetes on this setup requires building those images with certain options being passed to the images, as done [here](https://github.com/phnmnl/container-galaxy-k8s-runtime/blob/develop/simplified_galaxy_stable_container_creation.sh). Please note that you will want to have your own version of `Docker_init` (like the one [here](https://github.com/phnmnl/container-galaxy-k8s-runtime/blob/develop/Dockerfile_init)), where you can setup your flavouring, tools and other settings to personalize the Galaxy instance that you will be deploying.

## Variables

| Parameter | Description | Default |
| -------- | ----------- | ---- |
| `export_dir` | Export directory for Galaxy compose | `/export` |
| `galaxy.brand` | Branding text displayed on Galaxy | `k8s` |
| `galaxy.init.image.repository` | Repository for the docker image: `<server>/<owner>/<image-name>` for Galaxy init. | `pcm32/galaxy-stable-k8s-init` |
| `galaxy.init.image.tag` | Image tag for Galaxy init image. | `pcm32/galaxy-stable-k8s` |
| `galaxy.init.image.pullPolicy` | Pull policy for the Galaxy init image | `IfNotPresent` |
| `galaxy.init.resources` | k8s resources map for the init process | |
| `galaxy.backend.postgres` | This is probably not being used, or left for legacy purposes | `true` |
| `galaxy.image.repository` | Repository for the docker image: `<server>/<owner>/<image-name>` for Galaxy main process. | `pcm32/galaxy-stable-k8s` |
| `galaxy.image.tag` | Image tag for Galaxy image. | `latest` |
| `galaxy.image.pullPolicy` | Pull policy for the Galaxy image. | `IfNotPresent` |
| `galaxy.tools.destination` | Directory where tools are stored, possibly not needed and should be removed. | `/export/tools` |
| `galaxy.k8s.supp_groups` | Kubernetes supplemental group (this is probably a list), used for writing with adequate privileges to certain shared file systems | |
| `galaxy.k8s.fs_group` | Kubernetes file system group (this is probably a list), used for writing with adequate privileges to certain shared file systems | |
| `galaxy.admin.email` | Admin email to setup Galaxy with. | |
| `galaxy.admin.password` | Admin password to setup Galaxy with. | |
| `galaxy.admin.api_key` | Admin api_key to setup Galaxy with. | |
| `galaxy.admin.username` | Admin username to setup Galaxy with. | |
| `galaxy.admin.allow_user_creation` | Configures `allow_user_creation` Galaxy config environment variable. | `"True"` |
| `galaxy.smtp.server` | SMTP server for Galaxy password reset functionality ||
| `galaxy.smtp.username` | SMTP username for Galaxy password reset functionality ||
| `galaxy.smtp.password` | SMTP password for Galaxy password reset functionality ||
| `galaxy.smtp.email_from` | SMTP email_from for Galaxy password reset functionality ||
| `galaxy.smtp.ssl` | SMTP ssl for Galaxy password reset functionality ||
| `galaxy.instance_resource_url` | Incoming URL label for Galaxy password reset functionality, shown on reset email to identify instance. ||
| `galaxy.internal_port` | Internal port where the Galaxy container serves content. | `80` |
| `galaxy.node_port_exposed` | Internal port where the Galaxy container serves content. | `30700` |
| `galaxy.create_pvc` | Whether to create or not a PVC for Galaxy, defaults to true. | `true` |
| `galaxy.pvc.name` | Name for the PVC that Galaxy and scheduled jobs will use. | `galaxy-pvc` |
| `galaxy.pvc.capacity` | Amount of this that the PVC requests, such as "15Gi" | `15Gi` |
| `service.name` | Name to use for the k8s service exposing Galaxy | `galaxy-svc` |
| `service.type` | Type of k8s service for Galaxy | `NodePort` |
| `pv_minikube` | Whether to create a Persistent Volume in minikube or not. | `false` |
| `external_ingress_controller` | Whether to use an external ingress controller or the chart's provided one, when using ingresses. | `false` |
| `ingress.enabled` | Whether to enable ingress or not... seems redundant, should be fixed. | `false` |
| `ingress.hostname` | Hostname to construct ingress URL to respond to (hostname.domain). | `galaxy` |
| `ingress.domain` | Domain to construct ingress URL to respond to (hostname.domain). | `local` |
| `ingress.annotations` | | |
| `ingress.tls` | | |
| `resources` | Resources requests and limits (k8s) for the Galaxy container when running. | |
| `postgres_for_galaxy.db_password` | Password to use for postgres setup | `change_me` |
| `postgres_for_galaxy.postgres_pvc` | Name of the Persistent Volume Claim to use with postgres, by default the same as Galaxy | `galaxy-pvc` |
| `postgres_for_galaxy.subpath` | A subpath in the PV where the postgres mount will be done | |
| `legacy.pre_k8s_16` | Whether we are running on a Kubernetes setup below 1.6 | `false` |
| `rbac_needed` | Whether RBAC setups for the chart should be activated. | `false` |
| `use_proftpd` | Use proftpd or not | `true` |
| `use_condor` | Use condor or not | `false` |
| `proftpd.image.repository` | docker image for proftpd | |
| `proftpd.image.tag` | tag for the proftpd image set above | |
| `proftpd.passive_port.low` | Passive port minimum for proftpd | |
| `proftpd.passive_port.high` | Passive port maximum for proftpd | |
| `proftpd.use_sftp` | If set to true, use sftp instead of ftp | |
| `proftpd.service.name` | Name to be given for the proftpd k8s service | |
| `proftpd.generate_ssh_key` |  Whether to generate the ssh key for sftp access | |
| `proftpd.node_port_exposed` | Port opened on k8s nodes for exposing proftpd | |





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
