from hashlib import md5
from os import path as op
import os
from time import time
import urlparse
from django.conf import settings


def upload_to(instance, filename, prefix=None, unique=False):
    """ Auto generate name for File and Image fields.
    """
    basedir = 'storage/'

    ext = op.splitext(filename)[1]
    name = str(instance.pk or '') + filename + (str(time()) if unique else '')

    # We think that we use utf8 based OS file system
    filename = md5(name.encode('utf8')).hexdigest() + ext
    if prefix:
        basedir = op.join(basedir, prefix)
    return op.join(basedir, filename[:2], filename[2:4], filename)


def get_path_from_url(url, root=settings.MEDIA_ROOT, url_root=settings.MEDIA_URL):
    """ make filesystem path from url """
    if url.startswith(url_root):
        url = url[len(url_root):]  # strip media root url
    return os.path.normpath(os.path.join(root, url))


def get_url_from_path(path, root=settings.MEDIA_ROOT, url_root=settings.MEDIA_URL):
    """ make url from filesystem path """
    if path.startswith(root):
        path = path[len(root):]   # strip media root
    return urlparse.urljoin(root, path.replace('\\', '/'))
