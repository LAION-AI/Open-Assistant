FROM postgres:15

COPY ./scripts/create-db.sh /docker-entrypoint-initdb.d/
