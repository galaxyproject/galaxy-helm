# Galaxy Helm Charts

This repo contains [Helm charts]() for easily deploying Galaxy on top of Kubernetes, in a number of scenarios, as described below. The two minimal requirements to be able to use them are:
- Helm installed
- Access to a Kubernetes cluster
  - For development purposes or local tests, the local Minikube environment can be used.
  
## Available Helm Charts

Previously functionality was split in two charts, they have now been unified into the `galaxy` chart, which merges all functionality available on `galaxy-simple` and `galaxy-postgres-chart`, which are deprecated now. Newer features, such as privileged file system support, are only supported on the `galaxy` chart. The new `galaxy` chart can be used for development, testing and production environments and is highly configurable.

## Helm for the first time

If using helm for the first time, you will need to initialize the helm on the cluster and add the helm repo to the local helm directories:

```
$ helm init
$ helm list # call a few times until no error is shown, this is to wait for the tiller pod from helm to be running on the cluster.
$ helm repo add galaxy-helm-repo https://pcm32.github.io/galaxy-helm-charts
```

if you have done this once in the past, you might need, from time to time, to update the local repo, by doing:

```
$ helm repo update
```
  
## Deployment scenarios

Here we show different examples on how to deploy Galaxy on Kubernetes with these helm charts for Galaxy. Many of the options above can be combined, it only requires the correct settings on the `--set` part.

### SQLite local deploy on Minikube

```
$ helm install --set pv_minikube="yes" galaxy-helm-repo/galaxy
```

This will produce an instance accessible on the minukube ip (normally 192.168.99.100), port 30700.

### SQLite local deploy on Minikube for developers

If you are developing tools for Galaxy, and want to try them on the local setup shown above, you can override the contents of the tools and config folders used by the Galaxy instance to reflect your own settings:

```
$ helm install --set pv_minikube="yes",development_folder="/path/to/your/galaxy-folder-where-config-and-tools-folders-exists" galaxy-helm-repo/galaxy
```

There are some variations on how you provide that `development_folder` path based on the OS where you're hosting minikube.

On **macOS**, minikube mounts the host `/Users` onto `/Users` on the minikube VM, making all home folders available. This means that as long as the `/path/to/your/galaxy-folder` is within your home, the path to be used is transparently the same.

On **Linux**, minikube mounts the host `/home` onto `/hosthome` on the minikube VM, which means that if your galaxy folder is available somewhere inside your home directory, it will be available to the Kubernetes cluster, yet the path given to Helm needs to reflect what is visible inside the minikube VM. So, if your Galaxy folder (containing config and tools folder) is available at `/home/jdoe/devel/galaxy`, then the path given for `development_folder` should be `/hosthome/jdoe/devel/galaxy` (please notice the replacement of `/home` with `/hosthome`.

On **Windows**, the mount point inside the minikube VM changes from `C:\Users` to `/c/Users` (so files on `C:\Users\jdoe\devel\galaxy` would be visible on minikube and Kubernetes on `/c/Users/jdoe/devel/galaxy`) so the `development_folder` variable needs to be set accordingly.

This will produce an instance accessible on the minukube ip (normally 192.168.99.100), port 30700.

This will deploy an SQLite backend, so your Galaxy config files need to be coherent with that. If your configuration expects a Postgres backend, there are other configurations below that serve this purpose. 

In the current settings, if you do an `minikube ssh` to go inside the VM, you will notice that all the Galaxy operation files are available within `/data/galaxy_data` (for debugging purposes of tools for instance).

### SQLite local on Minikube using a different Galaxy container

```
$ helm install --set pv_minikube="yes",galaxy_image_registry="",galaxy_image="pcm32/galaxy-k8s-runtime",galaxy_image_tag=":v1" galaxy-helm-repo/galaxy
```

This will try to pull the image `pcm32/galaxy-k8s-runtime` from Dockerhub (which needs to be a Galaxy container compliant with our setup). If you are using a locally tagged image which you haven't pushed to Dockerhub, you can add `galaxy_pull_policy="IfNotPresent"` to the set commands. For working with local images, you will probably want to redirect your host's docker client to the minikube VM's docker engine, and use that to build the images. See the minikube documentation for more details on that.

### Postgresql local deploy on Minikube

```
$ helm install --debug --set pv_minikube="yes",galaxy_backend_postgres=true galaxy-helm-repo/galaxy
```

This will produce an instance accessible on the minukube ip (normally 192.168.99.100), port 30700. Postgresql will be the backend, running on a separate container. 

### With DNS set through an Ingress

If you have a domain name pointing to the IP of your cluster, you can make use of Kubernetes Ingress API object to redirect a particular "hostname" within that domain to your Galaxy running inside the Kubernetes cluster. 

```
$ helm install --set use_ingress="yes",hostname="galaxy",domain="mydomain.dev",galaxy_backend_postgres=true galaxy-helm-repo/galaxy
```

This will make you Galaxy service available on http://galaxy.mydomain.dev. This setup is using an internally provisioned `nginx` ingress controller/load balancer. If your Kubernetes cluster already has an Ingress controller, you can add the variable `external_ingress_controller="yes"` to avoid using the one included on this chart. While this example is given in the postgre section, it can be used as well with an sqlite backend.

### Securing the admin user

Provisioning instances that are publicly available might require, for security purposes, to set up an admin user for the Galaxy instance. This will also provoke that users can no longer sign up on their own, and it will require the newly set administrator to grant access. If this fits your setup needs, you can invoke the deployment in the following way:

```
$ helm install --set galaxy_admin_email="user@domain",galaxy_admin_password="six-character-password",galaxy_api_key="qwertyuio" galaxy-helm-repo/galaxy
```

This setup presumes that there is an available Persistent Volume provisioned which is concurrently accessible for read/write from all nodes (basically a shared filesystem, such as NFS or GlusterFS). This will create the instance, insert the API key, create the user with that password and set its email as admin. The injected API key will be removed then. Previously explained variables can be used as well with the ones introduced in this point.

### Documentation on additional functionality

More functionality in terms of variables that can be set can be found documented as part of the `values.yaml` file available inside each chart, or by invoking:

```
$ helm inspect galaxy-helm-repo/galaxy
```

# Experimental: using docker-galaxy-stable/compose images

## Simplest setup

**Currently not working** due to [this issue](https://github.com/bgruening/docker-galaxy-stable/issues/402) (or poor image pick for init when trying).

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

Please not the use of **galaxy-stable** at the end of the call, instead of **galaxy**. In time the **galaxy** chart used in previous examples will be deprecated in favour of **galaxy-stable**.

This will generate a galaxy instance available on any of the IPs of the Kubernetes clusters on port `30700`.

## Running PhenoMeNal using the compose images

Since the PhenoMeNal Galaxy instance was the precursor in the use of Galaxy within Kubernetes, this example has been tested more.

```
helm install -f example_configs/phenomenal-simple-config-galaxy-stable.yaml galaxy-helm-repo/galaxy-stable
```

This will generate a galaxy instance available on any of the IPs of the Kubernetes clusters on port `30700`.


# Funding

Most of this work, includng the Galaxy-Kubernetes integration, has been contributed to the community thanks to the funding of the European Comission (EC), through the PhenoMeNal H2020 Project, grant agreement number 654241.
