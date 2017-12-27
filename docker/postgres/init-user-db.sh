#!/bin/bash

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER scapi WITH PASSWORD 'password' CREATEDB;
    CREATE DATABASE scapi_dev;
    GRANT ALL PRIVILEGES ON DATABASE scapi_dev TO scapi;
EOSQL