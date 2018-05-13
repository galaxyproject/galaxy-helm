## Deployment scenarios

Here we show different examples on how to deploy Galaxy on Kubernetes with these helm charts for Galaxy. Many of the options above can be combined, it only requires the correct settings on the `--set` part or by using a configuration file written in YAML (preferred).

### SQLite local deploy on Minikube

```
$ helm install --set pv_minikube="yes" galaxy-helm-repo/galaxy
```

This will produce an instance accessible on the minukube ip (normally 192.168.99.100), port 30700.

This is also applicable for the `galaxy-stable` chart.

### SQLite local deploy on Minikube for developers

If you are developing tools for Galaxy, and want to try them on the local setup shown above, you can override the contents of the tools and config folders used by the Galaxy instance to reflect your own settings (only applicable currently for the `galaxy` chart, but not `galaxy-stable`:

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

### Using a different Galaxy container

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
