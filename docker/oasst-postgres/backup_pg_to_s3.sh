#!/bin/bash

set -e
set -x

# filename with timestamp
filename="postgres-$(date +%Y-%m-%d_%H-%M-%S).sql.gz"

# perform pg_dump
pg_dump -U postgres postgres | gzip -c > /tmp/$filename

# upload to s3
aws s3 cp /tmp/$filename s3://$S3_BUCKET_NAME/$filename

rm /tmp/$filename
