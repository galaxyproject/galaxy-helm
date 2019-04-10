# Galaxy Helm Chart (draft)

*The following is intended for use in* ***development mode only***

This is an initial draft of a galaxy helm chart.

## Usage

1. Install the [PostgreSQL chart](postgres)
```
helm dependency update
```

2. Create persistent volumes (+ claims)  `galaxy-pv`, `galaxy-pvc`, `galaxy-postgres-pv`, `galaxy-postgres-pvc`:
```
kubectl create -f volumes
```

3. Create configmap for initdb scripts:
```
kubectl create configmap galaxy-initdb --from-file=configmaps/initdb
```

4. To install the chart with the release name `galaxy`:
```
helm install --name galaxy .
```
In about 50 seconds, Galaxy will be available at https://localhost/. (Subsequent startup times are
about 25 seconds)

To delete the deployment, run:
```
helm del --purge galaxy
```
