# nnmware(c)2012-2016

import os

DIRNAME = os.path.dirname(__file__)
PROJECT_ROOT = os.path.normpath(os.path.dirname(__file__))

DJANGO_PROJECT = 'nnmware'
DJANGO_SETTINGS_MODULE = 'settings'
FORCE_SCRIPT_NAME = ''
DEBUG = True
LOCAL_DEV = True

ADMINS = [
    ('YOU NAME', 'user@mail.com'),
]

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'nnmware.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

LOCALE_PATHS = (
    '/usr/src/nnmware/locale',
)


TIME_ZONE = 'Europe/Moscow'
LANGUAGE_CODE = 'ru-ru'
SITE_ID = 1
USE_I18N = False

MEDIA_ROOT = '/usr/src/nnmware/media'
STATIC_ROOT = os.path.join(DIRNAME, 'static')
MEDIA_URL = '/m/'
STATIC_URL = '/static/'


STATICFILES_DIRS = [
    '/usr/src/nnmware/static',
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Don't share it with anybody
SECRET_FILE = os.path.join(DIRNAME, 'secret.txt')
try:
    SECRET_KEY = open(SECRET_FILE).read().strip()
except IOError:
    try:
        from random import choice
        key = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        SECRET_KEY = ''.join([choice(key) for i in range(50)])
        with open(SECRET_FILE, 'w') as secret:
            secret.write(SECRET_KEY)
    except IOError:
        raise Exception('Please create a %s file with random characters to generate your secret key!' % SECRET_FILE)

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'nnmware.core.backends.UsernameOrEmailAuthBackend',
]

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(DIRNAME, "templates"),
        ],
        # 'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.static',
                'django.template.context_processors.csrf',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': True,
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admindocs',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.syndication',
    'nnmware.core',
    'nnmware.apps.money',
    'nnmware.apps.booking',
    'nnmware.apps.market',
    'nnmware.apps.address',
    'nnmware.apps.dossier',
    'nnmware.apps.business',
    'nnmware.apps.realty',
    'nnmware.apps.transport',
    'nnmware.apps.publication',
    'nnmware.apps.topic',
    'nnmware.demo',
]

ABSOLUTE_URL_OVERRIDES = {
    'auth.user': lambda u: "/user/%s/" % u.username,
}

try:
    from nnmware_settings import *
except ImportError:
    import sys
    sys.stderr.write('No addition site config found (nnmware_settings.py\n')
    sys.exit(1)
