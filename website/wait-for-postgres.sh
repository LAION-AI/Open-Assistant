#!/bin/sh

# Wait for db & run migrations

# You don't need to provide the connection URL.  This reads it from the DATABASE_URL environment variable
# which should be set.

set -e

# validate schema
npx --yes prisma validate

# wait until the db is available
until echo 'SELECT version();' | npx prisma db execute --stdin; do
  echo >&2 "Postgres is unavailable - sleeping"
  sleep 1
done

echo >&2 "Postgres is up - applying migrations"

npx prisma migrate deploy

# Print and execute all other arguments starting with `$1`
# So `exec "$1" "$2" "$3" ...`
exec "$@"
