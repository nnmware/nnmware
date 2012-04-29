import os
import fnmatch
import shutil
import urlparse
from django.contrib import messages
from nnmware.core.middleware import get_request

try:
    import Image
except ImportError:
    import PIL as Image
from django.conf import settings
from django.core.cache import get_cache
from django.db.models.fields.files import ImageField
from nnmware.core.txtutil import URLify

image_cache = get_cache('locmem:///')

_FILE_CACHE_TIMEOUT = 60 * 60 * 60 * 24 * 31
_THUMBNAIL_GLOB = '%s_t*%s'


def _get_thumbnail_path(path, width=None, height=None):
    """ create thumbnail path from path and required width and/or height.

        thumbnail file name is constructed like this:
            <basename>_t_[w<width>][_h<height>].<extension>
    """

    # one of width/height is required
    assert (width is not None) or (height is not None)

    basedir = os.path.dirname(path) + '/'
    base, ext = os.path.splitext(os.path.basename(path))

    # make thumbnail filename
    th_name = base + '_t'
    if (width is not None) and (height is not None):
        th_name += '_w%d_h%d' % (width, height)
    elif width is not None:
        th_name += '%d' % width  # for compatibility with admin
    elif height is not None:
        th_name += '_h%d' % height
    th_name += ext

    return urlparse.urljoin(basedir, th_name)


def _get_path_from_url(url, root=settings.MEDIA_ROOT,
                       url_root=settings.MEDIA_URL):
    """ make filesystem path from url """

    #    if url.startswith('/'):
    #        return url

    if url.startswith(url_root):
        url = url[len(url_root):]  # strip media root url

    return os.path.normpath(os.path.join(root, url))


def _get_url_from_path(path, root=settings.MEDIA_ROOT,
                       url_root=settings.MEDIA_URL):
    """ make url from filesystem path """

    if path.startswith(root):
        path = path[len(root):]   # strip media root

    return urlparse.urljoin(root, path.replace('\\', '/'))


def _has_thumbnail(photo_url, width=None, height=None,
                   root=settings.MEDIA_ROOT, url_root=settings.MEDIA_URL):
    # one of width/height is required
    assert (width is not None) or (height is not None)

    return os.path.isfile(_get_path_from_url(_get_thumbnail_path(photo_url,
        width, height), root, url_root))


def make_thumbnail(photo_url, width=None, height=None,
                   root=settings.MEDIA_ROOT, url_root=settings.MEDIA_URL):
    """ create thumbnail """

    # one of width/height is required
    assert (width is not None) or (height is not None)

    if not photo_url:
        return None

    th_url = _get_thumbnail_path(photo_url, width, height)
    th_path = _get_path_from_url(th_url, root, url_root)
    photo_path = _get_path_from_url(photo_url, root, url_root)

    if _has_thumbnail(photo_url, width, height, root, url_root):
        # thumbnail already exists
        if not (os.path.getmtime(photo_path) > os.path.getmtime(th_path)):
            # if photo mtime is newer than thumbnail recreate thumbnail
            return th_url

    # make thumbnail

    # get original image size
    orig_w, orig_h = get_image_size(photo_url, root, url_root)
    if (orig_w is None) and (orig_h is None):
        # something is wrong with image
        return photo_url

    # make proper size
    if (width is not None) and (height is not None):
        if (orig_w == width) and (orig_h == height):
            # same dimensions
            return None
        size = (width, height)
    elif width is not None:
        if orig_w == width:
            # same dimensions
            return None
        size = (width, orig_h)
    elif height is not None:
        if orig_h == height:
            # same dimensions
            return None
        size = (orig_w, height)

    try:
        img = Image.open(photo_path).copy()
        img.thumbnail(size, Image.ANTIALIAS)
        img.save(th_path, quality=settings.THUMBNAIL_QUALITY)
    except Exception, err:
        # this goes to webserver error log
        import sys
        print >> sys.stderr, '[MAKE THUMBNAIL] error %s for file %r' % (err, photo_url)
        return photo_url

    return th_url


def remove_thumbnails(pic_url, root=settings.MEDIA_ROOT, url_root=settings.MEDIA_URL):
    if not pic_url:
        return  # empty url

    file_name = _get_path_from_url(pic_url, root, url_root)
    import fnmatch
    import os

    base, ext = os.path.splitext(os.path.basename(file_name))
    basedir = os.path.dirname(file_name)
    for file in fnmatch.filter(os.listdir(str(basedir)), _THUMBNAIL_GLOB % (base, ext)):
        path = os.path.join(basedir, file)
#        try:
        os.remove(path)
#        except OSError:
            # no reason to crash due to bad paths.
#            messages.error(get_request(), "Could not delete image thumbnail: %s", path)

def resize_image(img_url, width=400, height=400, root=settings.MEDIA_ROOT, url_root=settings.MEDIA_URL):
    file_name = _get_path_from_url(img_url, root, url_root)
    im = Image.open(file_name)
    if im.size[0] > width or im.size[1] > height:
        im.thumbnail((width, height), Image.ANTIALIAS )
    im.save(file_name, "JPEG", quality=88 )


def remove_file(f_url, root=settings.MEDIA_ROOT, url_root=settings.MEDIA_URL):
    if not f_url:
        return   # empty url
    file_name = _get_path_from_url(f_url, root, url_root)
    try:
        os.remove(file_name)
    except:
        messages.error(get_request(), "Could not delete file: %s", file_name)


def make_admin_thumbnail(url):
    """ make thumbnails for admin interface """
    return make_thumbnail(url, width=120)


def make_admin_thumbnails(model):
    """ create thumbnails for admin interface for all ImageFields
    (and subclasses) in the model """

    for obj in model._meta.fields:
        if isinstance(obj, ImageField):
            url = getattr(model, obj.name).path
            make_thumbnail(url, width=120)


def _get_thumbnail_url(photo_url, width=None, height=None, root=settings.MEDIA_ROOT, url_root=settings.MEDIA_URL):
    """ return thumbnail URL for requested photo_url and required
    width and/or height

        if thumbnail file do not exists returns original URL
    """

    # one of width/height is required
    assert (width is not None) or (height is not None)

    if _has_thumbnail(photo_url, width, height, root, url_root):
        return _get_thumbnail_path(photo_url, width, height)
    else:
        return photo_url


def _set_cached_file(path, value):
    """ Store file dependent data in cache.
        Timeout is set to _FILE_CACHE_TIMEOUT (1month).
    """

    mtime = os.path.getmtime(path)
    image_cache.set(path, (mtime, value,), _FILE_CACHE_TIMEOUT)


def _get_cached_file(path, default=None):
    """ Get file content from cache.
        If modification time differ return None and delete
        data from cache.
    """

    cached = image_cache.get(path, default)
    if cached is None:
        return None
    mtime, value = cached

    if (not os.path.isfile(path)) or (os.path.getmtime(path) != mtime):
        # file is changed or deleted
        image_cache.delete(path)  # delete from cache
        # remove thumbnails if exists
        base, ext = os.path.splitext(os.path.basename(path))
        basedir = os.path.dirname(path)
        for file in fnmatch.filter(os.listdir(basedir), _THUMBNAIL_GLOB % (base, ext)):
            os.remove(os.path.join(basedir, file))
        return None
    else:
        return value


def get_image_size(photo_url, root=settings.MEDIA_ROOT, url_root=settings.MEDIA_URL):
    """ returns image size.

        image sizes are cached (using separate locmem:/// cache instance)
    """

    path = _get_path_from_url(photo_url, root, url_root)

    size = _get_cached_file(path)
    if size is None:
        try:
            size = Image.open(path).size
        except Exception, err:
            # this goes to webserver error log
            import sys
            print >> sys.stderr, '[GET IMAGE SIZE] error %s for file %r' % (err, photo_url)
            return None, None
        if size is not None:
            _set_cached_file(path, size)
        else:
            return None, None

    return size


##################################################
## FILE HELPERS ##

def _rename(old_name, new_name):
    """ rename image old_name -> name """
    try:
        shutil.move(os.path.join(settings.MEDIA_ROOT, old_name), os.path.join(settings.MEDIA_ROOT, new_name))
        return new_name
    except IOError:
        return old_name


def rename_by_field(file_path, req_name, add_path=None):
    if file_path.strip() == '':
        return ''   # no file uploaded

    old_name = os.path.basename(file_path)
    path = os.path.dirname(file_path)

    media_root = os.path.normpath(settings.MEDIA_ROOT)
    if path.startswith(media_root):
        path = path[len(media_root):]
    if path[0] == '/':
        path = path[1:]

    name, ext = os.path.splitext(old_name)
    new_name = URLify(req_name) + ext

    if (add_path is not None) and (add_path not in path):
    # prevent adding if already here
        dest_path = os.path.join(path, add_path)
    else:
        dest_path = path

    if not os.path.isdir(os.path.join(media_root, dest_path)):
        os.mkdir(os.path.join(media_root, dest_path))

    dest_path = os.path.join(dest_path, new_name)

    if file_path != dest_path:
        return _rename(file_path, dest_path).replace('\\', '/')   # windows fix
    else:
        return file_path.replace('\\', '/')  # windows fix

def fit(image, size):
    # Resize Image not more then SIZEpx width.. or Enlarge Image is smaller then SIZE
    wpercent = (size / float(image.size[0]))
    hsize = int((float(image.size[1]) * float(wpercent)))
    image = image.resize((size, hsize), Image.ANTIALIAS)
    return image

def aspect_ratio(image, w, h):
    # Function for make Aspect Ratio of Image(i.e 16:9)
    imageWidth=image.size[0]
    imageHeight=image.size[1]
    newImageHeight = int((imageWidth/w) * h)
    topCrop = int((imageHeight-newImageHeight)/2)
    bottomCrop= imageHeight-topCrop
    box = (0, topCrop, imageWidth, bottomCrop)
    image = image.crop(box)
    return image

def get_thumbnail_path(url,size):
    url_t = make_thumbnail(url, width=size)
    return _get_path_from_url(url_t)
