# Galaxy Helm Chart (draft)

*The following is intended for use in* ***development mode only***

This is an initial draft of a galaxy helm chart.

## Usage

1. Install the required dependency charts.
```
helm dependency update
```

2. Create a persistent volume and claim for the database. This needs to be
done only once.
```
kubectl create -f postgres-pv.yaml
```

3. To install the chart with the release name `galaxy`:
```
helm install --name galaxy .
```
In about 50 seconds, Galaxy will be available at https://localhost/.
Subsequent startup times are about 25 seconds.

To delete the deployment, run:
```
helm del --purge galaxy
```
