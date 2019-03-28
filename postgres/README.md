# PostgreSQL Helm Chart Helper

*The following is intended for use in* ***development mode only***

This helper installs the [Bitnami PostgreSQL helm
chart](https://github.com/helm/charts/tree/master/stable/postgresql) 
that uses the [Docker Official PostgreSQL image](https://hub.docker.com/_/postgres) and a preloaded
Galaxy database.

## Usage

1. The database `data` directory should be located on the host at the path specified in
   `postgres-pv.yaml` (at `.spec.hostPath.path`). 
   The default value is `/tmp/docker/volumes/galaxy_postgres`.

   The galaxy database must be preloaded. (archive available at ...). 

2. Create a persistent volume `galaxy-postgres-pv` and persistent volume claim `galaxy-postgres-pvc`:
```
kubectl create -f postgres-pv.yaml
```

3. To install the chart with the release name `galaxy-postgres` and the provided `values.yaml` file:
```
helm install --name galaxy-postgres -f values.yaml stable/postgresql
```
```
```
To delete the chart with the release name `galaxy-postgres` and the provided `values.yaml` file:
```
helm delete --purge galaxy-postgres
```
Both commands are available as `install` and `delete` shell scripts.

## Notes

The preloaded `galaxy` database should have a user `galaxydbuser` with read/write privileges to all
tables and sequences within the `galaxy` database. Password authentication mode should be enabled
for this user/database.
