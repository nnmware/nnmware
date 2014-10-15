# -*- encoding: utf-8 -*-

# This file is used to store your site specific settings
# for database access.
# It also store nnmware unique information
#

GRAPPELLI_ADMIN_TITLE = 'NNMWARE@2014 framework for python/django coders'
GRAPPELLI_INDEX_DASHBOARD = 'dashboard.NnmwareDashboard'
LANGUAGE_COOKIE_NAME = 'nnmware_language'
LOGIN_ERROR_URL = '/login/error/'

# Site account settings
LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/'
AUTH_USER_MODEL = "demo.User"
PROFILE_DEFAULT_TIME_ZONE = 10
SITENAME = 'NNMWARE.COM'

CAPTCHA_ENABLED = True
REQUIRE_EMAIL_CONFIRMATION = False
DATETIME_FORMAT = 'd M Y  H:i:s'

EMAIL_USE_TLS = True
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'test@localhost'
EMAIL_HOST_PASSWORD = 'pass'

# These are used when loading the test data
SITE_DOMAIN = "NNMWARE TEST"
SITE_NAME = "NNMWARE TEST"

# These can override or add to the default URLs
from django.conf.urls import *

URLS = patterns('',)
APPEND_SLASH = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/nnmware_cache',
        'TIMEOUT': 60,
        'OPTIONS': {'MAX_ENTRIES': 1000}
    }
}
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 600
CACHE_MIDDLEWARE_KEY_PREFIX = ''


# Configure logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
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
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/nnmware.log',
        }

    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}

