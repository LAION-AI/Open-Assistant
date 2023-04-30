#!/bin/sh

# Wait for db & run migrations

# You don't need to provide the connection URL.  This reads it from the DATABASE_URL environment variable
# which should be set.

set -e

# validate schema
npx prisma validate

# wait until the db is available
until echo 'SELECT version();' | npx prisma db execute --stdin; do
  echo >&2 "Postgres is unavailable - sleeping"
  sleep 1
done

echo >&2 "Postgres is up - executing command"

# TODO: replace this command with applying migrations: npx prisma migrate deploy
# NOTE: because of our previous setup where we just synced the database, we have to "simulate"
# the initial migration with this command:
# npx prisma migrate resolve --applied 20230326131923_initial_migration
# prisma will fail with the above command if resolve is already applied,
# we might need to run the command with set +e
npx prisma db push --skip-generate

# Print and execute all other arguments starting with `$1`
# So `exec "$1" "$2" "$3" ...`
exec "$@"
