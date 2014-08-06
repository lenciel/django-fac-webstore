#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Production settings and globals."""


from os import environ

from .base import *

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

DEBUG = True

TEMPLATE_DEBUG = DEBUG

########## DJANGO SITE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#sites
SITE_ID = 1
SITE_NAME = 'stage.webstore.app2b.cn'

# 邮件接收地址
FAC_OFFICIAL_EMAIL = "zoomtest@163.com"

########## DATABASE CONFIGURATION
# CREATE DATABASE webstore;
# GRANT ALL ON webstore.* TO webstore@localhost IDENTIFIED BY 'f112b2d1d8c89';
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
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
########## END CACHE CONFIGURATION


########## SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = r"8(*14_f25=d%a)r78*qblk7lf-x!(da#!=^yz=-e#0y=^k69ra"
########## END SECRET CONFIGURATION

############## GOOGLE ANALYTICS CONFIGURATION ###############
# TODO: use correct id for stage.
GOOGLE_ANALYTICS_PROPERTY_ID = 'UA-44934150-6'
#############################################################
