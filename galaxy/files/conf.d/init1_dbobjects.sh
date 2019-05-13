#!/bin/bash

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRESQL_USERNAME" --dbname "$POSTGRESQL_DATABASE" <<-EOSQL
		CREATE DATABASE galaxy;
		CREATE USER galaxydbuser;
		ALTER ROLE galaxydbuser WITH PASSWORD '42';
		GRANT ALL PRIVILEGES ON DATABASE galaxy TO galaxydbuser;
		ALTER DATABASE galaxy OWNER TO galaxydbuser;
EOSQL
