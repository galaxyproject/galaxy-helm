# Galaxy Helm Chart

## Setup

1. Install the required dependency charts:
```
helm dependency update
```

2. Download a pre-built Postgres database, place it in a persistent
location on the host, and create a corresponding persistent volume & claim:
```
mkdir -p /tmp/k8s/volumes/ && cd "$_"
curl https://galaxy-helm-dev.s3.amazonaws.com/galaxy-db.tar.gz | tar -xz - && cd - && \
kubectl create -f postgres-pv.yaml
```

3. Install the chart, naming it `galaxy`:
```
helm install --name galaxy .
```

In about 20 seconds, Galaxy will be available at https://localhost/.

To delete the deployment, run:
```
helm del --purge galaxy
```
