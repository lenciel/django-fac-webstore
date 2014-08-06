#!/bin/sh
#
# Run 

if [ $# -eq 1 ]; then
  env=$1
else
  env=local
fi

if [ ! -d logs ]; then
  mkdir logs
fi

./manage.py runserver --settings=settings.$env 0:8000
