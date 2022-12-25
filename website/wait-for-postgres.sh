#!/bin/sh
# wait-for-postgres.sh
#
# This script tries to connect to a postgres database and then runs
#   `npx prisma db push`
# It repeats until that setup completes (running multiple times will be a
# noop).  Then, it'll run the next command provided.
#
# You don't need to provide the connection URL.  This reads it from the
# DATABASE_URL environment variable which should be set.
#
# To run we suggest:
#   ./wait-for-postgres.sh npm run dev

set -e

until npx prisma db push --skip-generate; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
# Print and execute all other arguments starting with `$1`
# So `exec "$1" "$2" "$3" ...`
exec "$@"
