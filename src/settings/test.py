#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .base import *

DEBUG = True

########## TEST SETTINGS
TEST_RUNNER = 'discover_runner.DiscoverRunner'
TEST_DISCOVER_TOP_LEVEL = SITE_ROOT
TEST_DISCOVER_ROOT = SITE_ROOT
TEST_DISCOVER_PATTERN = "test_*.py"

########## IN-MEMORY TEST DATABASE
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    },
}

INSTALLED_APPS += (
    'discover_runner',
    'django_jenkins',
    'django_extensions',
)

#NOTE: must remove "south" form install apps, otherwise loading fixture will be failed due to
# "Sync" intercepted by south.
apps_without_south = list(INSTALLED_APPS)
apps_without_south.remove('south')

INSTALLED_APPS = tuple(apps_without_south)

#
JENKINS_TASKS = (
    'django_jenkins.tasks.with_coverage',
    'django_jenkins.tasks.django_tests',   # select one django or
    'django_jenkins.tasks.dir_tests',      # directory tests discovery
    'django_jenkins.tasks.run_pep8',
    'django_jenkins.tasks.run_pyflakes',
    'django_jenkins.tasks.run_graphmodels',
    'django_jenkins.tasks.run_pylint',
    #'django_jenkins.tasks.run_csslint',
    'django_jenkins.tasks.run_sloccount',
    #'django_jenkins.tasks.run_jshint',
    #'django_jenkins.tasks.lettuce_tests',
)


