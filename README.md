# Galaxy Helm Charts

This repo contains [Helm charts]() for easily deploying Galaxy on top of Kubernetes, in a number of scenarios, as described below. The two minimal requirements to be able to use them are:
- Helm installed
- Access to a Kubernetes cluster
  - For development purposes or local tests, the local Minikube environment can be used.
  
## Available Helm Charts

Currently we have two separate helm charts: 

- `galaxy-simple` : aimed mostly at development enviroment, running on Minikube, although it can be run on other environments. It has only fixed support for sqlite. It has a number of options for filesystem provisioning, ingresses, container image to use, etc.
- `galaxy-postgres-chart` : aimed at production deployment, but can be as well installed locally on Minikube. It uses Postgres as a backend, and has many configurable options (secure the instance for a user, access through ip:port or DNS based, filesystem provisioning, etc).

We expect in the near future to unify both charts to reduce maintainance efforts.

## Helm for the first time

If using helm for the first time, you will need to initialize the helm on the cluster and add the helm repo to the local helm directories:

```
$ helm init
$ helm repo add galaxy-helm-repo https://pcm32.github.io/galaxy-helm-charts
```

if you have done this once in the past, you might need, from time to time, to update the local repo, by doing:

```
$ helm repo update
```
  
## Deployment scenarios

Here we show different examples on how to deploy Galaxy on Kubernetes with these helm charts for Galaxy. 

### SQLite local deploy on Minikube

```
$ helm install --set pv_minikube="yes" galaxy-helm-repo/galaxy-simple
```

This will produce an instance accessible on the minukube ip (normally 192.168.99.100), port 30700.

### SQLite local deploy on Minikube for developers

If you are developing tools for Galaxy, and want to try them on the local setup shown above, you can override the contents of the tools and config folders used by the Galaxy instance to reflect your own settings:

```
$ helm install --set pv_minikube="yes",development_folder="/path/to/your/galaxy-folder-where-config-and-tools-folders-exists" galaxy-helm-repo/galaxy-simple
```

There are some variations on how you provide that `development_folder` path based on the OS where you're hosting minikube.

On **macOS**, minikube mounts the host `/Users` onto `/Users` on the minikube VM, making all home folders available. This means that as long as the `/path/to/your/galaxy-folder` is within your home, the path to be used is transparently the same.

On **Linux**, minikube mounts the host `/home` onto `/hosthome` on the minikube VM, which means that if your galaxy folder is available somewhere inside your home directory, it will be available to the Kubernetes cluster, yet the path given to Helm needs to reflect what is visible inside the minikube VM. So, if your Galaxy folder (containing config and tools folder) is available at `/home/jdoe/devel/galaxy`, then the path given for `development_folder` should be `/hosthome/jdoe/devel/galaxy` (please notice the replacement of `/home` with `/hosthome`.

On **Windows**, the mount point inside the minikube VM changes from `C:\Users` to `/c/Users` (so files on `C:\Users\jdoe\devel\galaxy` would be visible on minikube and Kubernetes on `/c/Users/jdoe/devel/galaxy`) so the `development_folder` variable needs to be set accordingly.

This will produce an instance accessible on the minukube ip (normally 192.168.99.100), port 30700.

This will deploy an SQLite backend, so your Galaxy config files need to be coherent with that. If your configuration expects a Postgres backend, there are other configurations below that serve this purpose. 

### Postgresql local deploy on Minikube

```
$ helm install --debug --set pv_minikube="yes" galaxy-helm-repo/galaxy-postgres-chart
```

This will produce an instance accessible on the minukube ip (normally 192.168.99.100), port 30700. Postgresql will be the backend, running on a separate container.



# Funding

Most of this work, includng the Galaxy-Kubernetes integration, has been contributed to the community thanks to the funding of the European Comission (EC), through the PhenoMeNal H2020 Project, grant agreement number 654241.
