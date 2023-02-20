#!/usr/bin/env bash
if [ -z "$0" ]
then
   echo "Kill running Celery processes";
   kill -9 $(ps aux | grep celery | grep -v grep | awk '{print $2}' | tr '\n'  ' ') > /dev/null 2>&1

fi
celery -A oasst_backend beat -l info &
celery -A oasst_backend worker -l info &
# celery -A oasst_backend beat -l info --logfile=celery.beat.log --detach
# celery -A oasst_backend worker -l info --logfile=celery.log --detach
