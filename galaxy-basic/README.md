# Galaxy Helm Chart (draft)

*The following is intended for use in* ***development mode only***

This is an initial draft of a galaxy helm chart.

## Usage

1. Install the [PostgreSQL chart](postgres)

2. Create a persistent volume `galaxy-pv` and persistent volume claim `galaxy-pvc`:
```
kubectl create -f galaxy-pv.yaml
```
3. To install the chart with the release name `galaxy`:
```
helm install --name galaxy .
```

TODO: Docker image needs to be rebuilt with correct db connection URL.
