#!/bin/sh
#
# Clean temp files and migrations history.
#
# This script is only for local dev environment.
# When you drop you database and want to re-create it,
# run this script before 'syncdb',
# otherwise not all tables will be created.
#
suffixs=".log .pyc ~"
for suffix in $suffixs;
do
  find . -name "*$suffix" -type f -print -exec rm -f {} \;
done

#
# Remove migrations directories
#
# remove project dir
find . -type d -name migrations -exec rm -fr {} \;
# remove site-package dir
find $VIRTUAL_ENV/lib/python2.7/site-packages/ -type d -name migrations -exec rm -fr {} \;

