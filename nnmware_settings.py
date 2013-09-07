# -*- encoding: utf-8 -*-

# This file is used to store your site specific settings
# for database access.
# It also store nnmware unique information
#

import os
from PIL import Image
import settings

GRAPPELLI_ADMIN_TITLE = 'NNMWARE@2013 framework for python/django coders'
GRAPPELLI_INDEX_DASHBOARD = 'dashboard.NnmwareDashboard'
LANGUAGE_COOKIE_NAME = 'nnmware_language'
NNMWARE_INI_FILE =  os.path.join(settings.PROJECT_ROOT, 'nnmware.ini')
# Social settings 
TWITTER_CONSUMER_KEY              = ''
TWITTER_CONSUMER_SECRET           = ''

FACEBOOK_APP_ID                   = ''
FACEBOOK_API_SECRET               = ''
GOOGLE_OAUTH2_CLIENT_ID           = ''
GOOGLE_OAUTH2_CLIENT_SECRET       = ''
SOCIAL_AUTH_CREATE_USERS          = True
SOCIAL_AUTH_FORCE_RANDOM_USERNAME = False
SOCIAL_AUTH_DEFAULT_USERNAME      = 'socialauth_user'
SOCIAL_AUTH_COMPLETE_URL_NAME     = 'socialauth_complete'
LOGIN_ERROR_URL                   = '/login/error/'
SOCIAL_AUTH_ERROR_KEY             = 'socialauth_error'

SOCIAL_AUTH_PIPELINE = (
    'nnmware.apps.social.backends.pipeline.social.social_auth_user',
    'nnmware.apps.social.backends.pipeline.misc.save_status_to_session',
    'nnmware.apps.social.backends.pipeline.user.get_username',
    'nnmware.apps.social.backends.pipeline.user.create_user',
    'nnmware.apps.social.backends.pipeline.social.associate_user',
    'nnmware.apps.social.backends.pipeline.social.load_extra_data',
    'nnmware.apps.social.backends.pipeline.user.update_user_details',
)
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/welcome/step1/'

# Site account settings
LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/'
AUTH_USER_MODEL = "demo.User"
PROFILE_DEFAULT_TIME_ZONE = 10
ACCOUNT_ACTIVATION_DAYS = 7
SITENAME = 'NNMWARE.COM'

RATINGS_MIN = 1
RATINGS_MAX = 10

TAGS_MAX = 20

IMG_MAX_PER_OBJECT = getattr(settings, 'PIC_MAX_PER_OBJECT', 42)
DOC_MAX_PER_OBJECT = getattr(settings, 'DOC_MAX_PER_OBJECT', 42)
IMG_MAX_SIZE = getattr(settings, 'PIC_MAX_SIZE', 1024 * 1024)
IMG_THUMB_FORMAT = getattr(settings, 'PIC_THUMB_FORMAT', "JPEG")
IMG_THUMB_QUALITY = getattr(settings, 'PIC_THUMB_QUALITY', 85)
IMG_RESIZE_METHOD = getattr(settings, 'PIC_RESIZE_METHOD', Image.ANTIALIAS)
IMG_DEFAULT_SIZE = getattr(settings, 'PIC_DEFAULT_SIZE', 96)
IMG_ALLOWED_FILE_EXTS = getattr(settings, 'PIC_ALLOWED_FILE_EXTS', None)

IMG_UPLOAD_DIR = getattr(settings, 'IMG_UPLOAD_DIR', 'img')
DOC_UPLOAD_DIR = getattr(settings, 'DOC_UPLOAD_DIR', 'doc')
AVATAR_UPLOAD_DIR = getattr(settings, 'DOC_UPLOAD_DIR', 'doc')
IMG_UPLOAD_SIZE = getattr(settings, 'IMG_UPLOAD_SIZE', 10485760)
DOC_UPLOAD_SIZE = getattr(settings, 'DOC_UPLOAD_SIZE', 10485760)

AVATAR_UPLOAD_DIR = getattr(settings, 'AVATAR_UPLOAD_DIR', 'avatar')
AVATAR_UPLOAD_SIZE = getattr(settings, 'AVATAR_UPLOAD_SIZE', 10485760)

THUMBNAIL_DIR = getattr(settings, 'THUMBNAIL_DIR', 'thumbnail')
AVATARS_DIR = getattr(settings, 'AVATARS_DIR', 'avatars')

DEFAULT_AVATAR = os.path.join(settings.MEDIA_URL, 'generic.png')
DEFAULT_AVATAR_WIDTH = 96
CAPTCHA_ENABLED = True
SITE_PROTOCOL = 'http'
REQUIRE_EMAIL_CONFIRMATION = False
DATETIME_FORMAT = 'd M Y  H:i:s'

##### For Email ########

EMAIL_USE_TLS = True
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'test@localhost'
EMAIL_HOST_PASSWORD = 'pass'

#These are used when loading the test data
SITE_DOMAIN = "NNMWARE TEST"
SITE_NAME = "NNMWARE TEST"

# These can override or add to the default URLs
from django.conf.urls import *

URLS = patterns('',
)
APPEND_SLASH = True
PAGINATE_BY = 10
PAGINATE_BOARD = 2

NAME_LENGTH = 256
DATE_FORMAT = "j.m.Y"
TIME_FORMAT = "G:i"
ACTION_RECORD_DAYS = 3

# Image settings
THUMBNAIL_QUALITY = 85

# Rename images?"),
# Automatically rename images on upload?
RENAME_IMAGES = True

WYSIWYG_ENABLE = True

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


#Configure logging
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
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
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
            'handlers':['null'],
            'propagate': True,
            'level':'INFO',
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}

