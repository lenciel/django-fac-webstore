#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Production settings and globals."""


from os import environ
from base import *

# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
from django.core.exceptions import ImproperlyConfigured


def get_env_setting(setting):
    """ Get the environment setting or return exception """
    try:
        return environ[setting]
    except KeyError:
        error_msg = "Set the %s env variable" % setting
        raise ImproperlyConfigured(error_msg)

########## DJANGO SITE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#sites
SITE_ID = 2
SITE_NAME = 'webstore.app2b.cn'

########## DATABASE CONFIGURATION
# CREATE DATABASE SITE_NAME;
# GRANT ALL ON SITE_NAME.* TO SITE_NAME@localhost IDENTIFIED BY 'f112b2d1d8c89';
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'webstore',
        'USER': 'webstore',
        'PASSWORD': 'f112b2d1d8c89',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

########## END DATABASE CONFIGURATION


########## CACHE CONFIGURATION
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

########## END CACHE CONFIGURATION

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

########## SITE CONFIGURATION
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['stage.webstore.app2b.cn', '42.62.56.115', 'webstore.app2b.cn', 'ws.app2b.cn']
########## END SITE CONFIGURATION


############## GOOGLE ANALYTICS CONFIGURATION ###############
GOOGLE_ANALYTICS_PROPERTY_ID = 'UA-44934150-7'
#############################################################