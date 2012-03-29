from hashlib import md5
from os import path as op
from time import time


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
