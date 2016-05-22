# nnmware(c)2012-2016

from __future__ import unicode_literals
from io import StringIO
import os
from hashlib import md5
from urllib.request import urlopen
from urllib.parse import urlparse
from PIL import Image

from django.conf import settings
from django.contrib.auth import get_user_model

from nnmware.core.imgutil import fit, aspect_ratio
from nnmware.core.utils import get_date_directory, setting


class EmailAuthBackend(object):
    """
    Email Authentication Backend
    
    Allows a user to sign in using an email/password pair rather than
    a username/password pair.
    """

    supports_inactive_user = False

    def authenticate(self, username=None, password=None):
        """ Authenticate a user based on email address as the user name. """
        # noinspection PyBroadException
        try:
            user = get_user_model().objects.get(email=username)
            if user.check_password(password):
                return user
        except:
            return None

    def get_user(self, user_id):
        """ Get a User object from the user_id. """
        # noinspection PyBroadException
        try:
            return get_user_model().objects.get(pk=user_id)
        except:
            return None


class UsernameOrEmailAuthBackend(object):

    def authenticate(self, username=None, password=None):
        if '@' in username:
            kwargs = {'email': username}
        else:
            kwargs = {'username': username}
        # noinspection PyBroadException
        try:
            user = get_user_model().objects.get(**kwargs)
            if user.check_password(password):
                return user
        except:
            return None

    def get_user(self, user_id):
        """ Get a User object from the user_id. """
        # noinspection PyBroadException
        try:
            return get_user_model().objects.get(pk=user_id)
        except:
            return None


def image_from_url(url):
    upload_dir = setting('THUMBNAIL_DIR', 'thumbnails')
    img_file = urlopen(url)
    im = StringIO(img_file.read())
    image = Image.open(im)
    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')
    image = fit(image, 300)
    image = aspect_ratio(image, 16, 9)
    timedir = get_date_directory()
    filename = urlparse(url).path.split('/')[-1]
    ext = os.path.splitext(filename)[1]
    new_filename = md5(filename.encode('utf8')).hexdigest() + ext
    path = os.path.join(settings.MEDIA_ROOT, upload_dir, timedir, new_filename)
    # noinspection PyBroadException
    try:
        os.makedirs(os.path.realpath(os.path.dirname(path)))
    except:
        pass
    image.save(path, 'jpeg')
    return upload_dir + "/" + timedir + "/" + new_filename
