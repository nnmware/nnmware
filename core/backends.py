from cStringIO import StringIO
from datetime import datetime
from io import FileIO, BufferedWriter
import os
from hashlib import md5
import urllib2
from urlparse import urlparse
from PIL import Image
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import check_password

from nnmware.core.imgutil import fit, aspect_ratio
from nnmware.core.utils import get_date_directory


class EmailAuthBackend(object):
    """
    Email Authentication Backend
    
    Allows a user to sign in using an email/password pair rather than
    a username/password pair.
    """

    supports_inactive_user = False

    def authenticate(self, username=None, password=None):
        """ Authenticate a user based on email address as the user name. """
        try:
            user = get_user_model().objects.get(email=username)
            if user.check_password(password):
                return user
        except:
            return None

    def get_user(self, user_id):
        """ Get a User object from the user_id. """
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
        try:
            user = get_user_model().objects.get(**kwargs)
            if user.check_password(password):
                return user
        except:
            return None

    def get_user(self, user_id):
        """ Get a User object from the user_id. """
        try:
            return get_user_model().objects.get(pk=user_id)
        except:
            return None


class AbstractUploadBackend(object):
    BUFFER_SIZE = 10485760  # 10MB

    def __init__(self, **kwargs):
        self._timedir = get_date_directory()
        self.__dict__.update(kwargs)

    def update_filename(self, request, filename):
        """Returns a new name for the file being uploaded."""
        self.oldname = filename
        ext = os.path.splitext(filename)[1]
        return md5(filename.encode('utf8')).hexdigest() + ext

    def upload_chunk(self, chunk):
        """Called when a string was read from the client, responsible for
        writing that string to the destination file."""
        self._dest.write(chunk)

    def max_size(self):
        """
        Checking file max size
        """
        if int(self._dest.tell()) > self.upload_size:
            self._dest.close()
            os.remove(self._path)
            return True

    def upload(self, uploaded, filename, raw_data):
        try:
            if raw_data:
                # File was uploaded via ajax, and is streaming in.
                chunk = uploaded.read(self.BUFFER_SIZE)
                while len(chunk) > 0:
                    self.upload_chunk(chunk)
                    if self.max_size():
                        return False
                    chunk = uploaded.read(self.BUFFER_SIZE)
            else:
                # File was uploaded via a POST, and is here.
                for chunk in uploaded.chunks():
                    self.upload_chunk(chunk)
                    if self.max_size():
                        return False
            return True
        except:
            # things went badly.
            return False

    def setup(self, filename):
        self._path = os.path.join(settings.MEDIA_ROOT, self.upload_dir, self._timedir, filename)
        try:
            os.makedirs(os.path.realpath(os.path.dirname(self._path)))
        except:
            pass
        self._dest = BufferedWriter(FileIO(self._path, "w"))

    def upload_complete(self, request, filename):
        path = self.upload_dir + "/" + self._timedir + "/" + filename
        self._dest.close()
        return {"path": path, 'oldname': self.oldname}


class DocUploadBackend(AbstractUploadBackend):
    upload_dir = settings.DOC_UPLOAD_DIR
    upload_size = settings.DOC_UPLOAD_SIZE


class PicUploadBackend(AbstractUploadBackend):
    upload_dir = settings.PIC_UPLOAD_DIR
    upload_size = settings.PIC_UPLOAD_SIZE


class AvatarUploadBackend(AbstractUploadBackend):
    upload_dir = settings.AVATAR_UPLOAD_DIR
    upload_size = settings.AVATAR_UPLOAD_SIZE


class ImgUploadBackend(AbstractUploadBackend):
    upload_dir = settings.IMG_UPLOAD_DIR
    upload_size = settings.IMG_UPLOAD_SIZE


def image_from_url(url):
    upload_dir = settings.THUMBNAIL_DIR
    img_file = urllib2.urlopen(url)
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
    try:
        os.makedirs(os.path.realpath(os.path.dirname(path)))
    except:
        pass
    image.save(path, 'jpeg')
    return upload_dir + "/" + timedir + "/" + new_filename


def upload_avatar_dir(instance, filename):
    upload_dir = settings.AVATARS_DIR
    new_filename = md5(filename.encode('utf8')).hexdigest() + os.path.splitext(filename)[1]
    timedir = get_date_directory()
    return upload_dir + "/" + timedir + "/" + new_filename


def upload_media_dir(instance, filename):
    upload_dir = settings.MEDIAFILES
    new_filename = md5(filename.encode('utf8')).hexdigest() + os.path.splitext(filename)[1]
    timedir = get_date_directory()
    return upload_dir + "/" + timedir + "/" + new_filename
