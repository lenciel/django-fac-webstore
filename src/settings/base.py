#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Common settings and globals."""
from sys import path

import os
from os.path import abspath, basename, dirname, join, normpath
from django.utils.translation import ugettext_lazy as _



########## PATH CONFIGURATION
# Absolute filesystem path to the Django project directory:
DJANGO_ROOT = dirname(dirname(abspath(__file__)))

# Absolute filesystem path to the top-level project folder:
SITE_ROOT = dirname(DJANGO_ROOT)

# Absolute filesystem path to the apps folder
APP_ROOT = join(DJANGO_ROOT, 'apps')

# Site name:
SITE_NAME = basename(DJANGO_ROOT)

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(DJANGO_ROOT)
########## END PATH CONFIGURATION


########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = False

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
########## END DEBUG CONFIGURATION


########## MANAGER CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (
    ('Your Name', 'your_email@example.com'),
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS
########## END MANAGER CONFIGURATION

########## GENERAL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
TIME_ZONE = 'Asia/Chongqing'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'zh-cn'

# See: https://docs.djangoproject.com/en/dev/topics/i18n/translation/#other-tags
LANGUAGES = (
    ('zh-cn', _('Chinese Simplified')),
    ('en', _('English'))
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = False

# See: https://docs.djangoproject.com/en/dev/ref/settings/#default-charset
DEFAULT_CHARSET = 'utf-8'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-LOCALE_PATHS
LOCALE_PATHS = join(DJANGO_ROOT, 'settings', 'locale')
########## END GENERAL CONFIGURATION

########## MEDIA CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = normpath(join(SITE_ROOT, 'media'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'

# the image folder name under MEDIA_ROOT
MEDIA_IMAGE_PREFIX = 'images'

# the content folder name under MEDIA_ROOT
MEDIA_CONTENT_PREFIX = 'contents'

if not os.path.exists(MEDIA_ROOT):
    os.mkdir(MEDIA_ROOT)
    os.mkdir(os.path.join(MEDIA_ROOT, MEDIA_IMAGE_PREFIX))
    os.mkdir(os.path.join(MEDIA_ROOT, MEDIA_CONTENT_PREFIX))

########## END MEDIA CONFIGURATION


########## STATIC FILE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = normpath(join(SITE_ROOT, 'assets'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    normpath(join(DJANGO_ROOT, 'static')),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# a default image for content title
STATIC_DEFAULT_TITLE_IMAGE_URL = ''

########## END STATIC FILE CONFIGURATION


########## SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = r"8(*14_f25=d%a)r_%78*qblk7lf-x!(da#!=^yz=-e#0y=^k69ra"
########## END SECRET CONFIGURATION

########## END SECRET CONFIGURATION

########## SITE CONFIGURATION
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []
########## END SITE CONFIGURATION


########## FIXTURE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    normpath(join(SITE_ROOT, 'fixtures')),
)
########## END FIXTURE CONFIGURATION


########## TEMPLATE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'apps.website.context_processor.ga_property_id',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
TEMPLATE_DIRS = (
    normpath(join(DJANGO_ROOT, 'templates')),
)
########## END TEMPLATE CONFIGURATION


########## MIDDLEWARE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#middleware-classes
MIDDLEWARE_CLASSES = (
    # Default Django middleware.
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # convert the ajax exception to given formation which is known by frontend
    'apps.common.exceptions.AjaxExceptionMiddleware',
)
########## END MIDDLEWARE CONFIGURATION


########## URL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = 'apps.urls'
########## END URL CONFIGURATION


########## APP CONFIGURATION
INSTALLED_APPS = (
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Useful template tags:
    # 'django.contrib.humanize',

    # Admin panel and documentation:
    'django.contrib.admin',
    # 'django.contrib.admindocs',
)

INSTALLED_APPS += (
    # Database migration helpers:
    'south',
    # Captcha images
    'captcha',
)

PROJECT_APPS = (
    'apps.common',
    'apps.account',
    'apps.admin',
    'apps.website',
    'apps.foundation',
    'apps.product',
    'apps.customer',
    'apps.order',
    'apps.wechat',
    'apps.payment',
    'apps.cms',
)

# Apps specific for this project go here.
INSTALLED_APPS += PROJECT_APPS

########## END APP CONFIGURATION


########## LOGGING CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
DEFAULT_LOG_FILE = join(SITE_ROOT, 'logs', 'django.log')
REQUEST_LOG_FILE = join(SITE_ROOT, 'logs', 'django_request.log')
if not os.path.exists(dirname(DEFAULT_LOG_FILE)):
    os.mkdir(dirname(DEFAULT_LOG_FILE))


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s [%(name)s.%(module)s] %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'default_log_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': DEFAULT_LOG_FILE,
            'maxBytes': 16777216, # 16megabytes
            'backupCount': 5,
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'include_html': True,
        },
        'request_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': REQUEST_LOG_FILE,
            'maxBytes': 1024 * 1024 * 5, # 5 MB
            'backupCount': 5,
            'formatter': 'simple',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default_log_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['request_handler'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'test': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        }
    }
}
########## END LOGGING CONFIGURATION

########## Session CONFIGURATION
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

SESSION_COOKIE_AGE = 86400

SESSION_COOKIE_AGE_15_DAY = 1296000
########## END Session CONFIGURATION

########## WSGI CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'settings.wsgi.application'
########## END WSGI CONFIGURATION

AUTH_USER_MODEL = 'account.User'

########## EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.exmail.qq.com')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-password
#EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '189worksCOM')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '189worksCOM')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#default-from-email
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'service@189works.com')

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = os.environ.get('EMAIL_PORT', 25)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = u'天翼空间应用工厂'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-use-tls
EMAIL_USE_TLS = False

# See: https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = EMAIL_HOST_USER

#webstore官方邮箱地址.
FAC_OFFICIAL_EMAIL = 'business@app2b.cn'
########## END EMAIL CONFIGURATION


############## WeChat Configuration
# Wehat token, keep it secret.
WECHAT_TOKEN = 'B6159B2C629C0D64AA1B9B894A818A3C'
WECHAT_APPID = 'wx36ad48a4256b1be1'
WECHAT_SECRET = 'c7f862e4bba49333b008a24c615515cf'
# 在access token失效前多长时间更新access token
WECHAT_TIME_TO_REFRESH_BEFORE_ACCESS_TOKEN_EXPIRE_IN_SECONDS = 240
############## End WeChat Configuration

############## GOOGLE ANALYTICS CONFIGURATION ###############
GOOGLE_ANALYTICS_PROPERTY_ID = 'UA-44934150-6'
#############################################################