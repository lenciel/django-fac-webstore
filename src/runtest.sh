#!/bin/sh
#
# Run unit tests
#
#./manage.py test report

#APPS="account report"
#coverage run --source="." manage.py test $APPS

coverage run --branch --include="apps/*" --omit="*migration*" manage.py test --settings=settings.test
ret=$?

# Run following command to get html coverage in htmlcov/
echo "Generating coverage html report on htmlcov/"
coverage html

exit $ret
