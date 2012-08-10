import os, sys
path = '/usr/src/nnmware'
if path not in sys.path:
    sys.path.append(path)
os.environ['PYTHON_EGG_CACHE']= '/tmp/nnmware-eggs'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
