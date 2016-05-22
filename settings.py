# nnmware(c)2012-2016

import os

DIRNAME = os.path.dirname(__file__)
PROJECT_ROOT = os.path.normpath(os.path.dirname(__file__))

DJANGO_PROJECT = 'nnmware'
DJANGO_SETTINGS_MODULE = 'settings'
FORCE_SCRIPT_NAME = ''
DEBUG = True
LOCAL_DEV = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('YOU NAME', 'user@mail.com'),
)

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


STATICFILES_DIRS = (
    '/usr/src/nnmware/static',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

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

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader')


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'nnmware.core.backends.UsernameOrEmailAuthBackend',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(DIRNAME, "templates"),
)

# this is used to add additional config variables to each request
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.static',
    'django.core.context_processors.csrf',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
)

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

INSTALLED_APPS = (
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
    'nnmware.demo',
)

ABSOLUTE_URL_OVERRIDES = {
    'auth.user': lambda u: "/user/%s/" % u.username,
}


try:
    from nnmware_settings import *
except ImportError:
    import sys
    sys.stderr.write('No addition site config found (nnmware_settings.py\n')
    sys.exit(1)
