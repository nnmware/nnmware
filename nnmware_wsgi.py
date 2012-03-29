import os
import sys
path = '/var/www/nnmware'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'nnmware.settings'
os.environ['PYTHON_EGG_CACHE']= '/tmp/trac-eggs'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
