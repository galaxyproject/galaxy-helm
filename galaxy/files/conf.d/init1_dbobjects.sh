#!/bin/bash

set -e

psql -v ON_ERROR_STOP=1 -v GXYPASSWORD="'$GALAXY_DB_USER_PASSWORD'" --username "$POSTGRESQL_USERNAME" --dbname "$POSTGRESQL_DATABASE" <<-EOSQL
		CREATE DATABASE galaxy;
		CREATE USER {{.Values.postgresql.galaxyDatabaseUser}};
		ALTER ROLE {{.Values.postgresql.galaxyDatabaseUser}} WITH PASSWORD :GXYPASSWORD;
		GRANT ALL PRIVILEGES ON DATABASE galaxy TO {{.Values.postgresql.galaxyDatabaseUser}};
		ALTER DATABASE galaxy OWNER TO {{.Values.postgresql.galaxyDatabaseUser}};
EOSQL
