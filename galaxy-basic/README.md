# Galaxy Helm Chart (draft)

*The following is intended for use in* ***development mode only***

This is an initial draft of a Galaxy Helm chart.

## Usage

1. Install the required PostgreSQL chart:
```
helm dependency update
```

2. Download a pre-migrated database to the following directory on the host:
```
mkdir -p /tmp/docker/volumes/ && cd "$_"
curl https://galaxy-helm-dev.s3.amazonaws.com/galaxy-db.tar.gz | tar -xz -
```

3. Create a persistent volumes and claims for Galaxy and Postgres:
```
kubectl create -f galaxy-pv.yaml
kubectl create -f galaxy-postgres-pv.yaml
```

4. To install the chart with the release name `galaxy`:
```
kubectl create configmap galaxy-initdb --from-file=configmaps/initdb
```

Galaxy will be available at https://localhost/.

To delete the deployment, run
```
helm del --purge galaxy
```

TODO: Docker image needs to be rebuilt with correct db connection URL.
