#!/usr/bin/env bash
if [ -z "$0" ]
then
   echo "Kill running Celery processes";
   kill -9 $(ps aux | grep celery | grep -v grep | awk '{print $2}' | tr '\n'  ' ') > /dev/null 2>&1

fi
cd ../../backend/oasst_backend
celery -A celery_worker beat -l info &
celery -A celery_worker worker -l info &
# celery -A celery_worker beat -l info --logfile=celery.beat.log --detach
# celery -A celery_worker worker -l info --logfile=celery.log --detach
