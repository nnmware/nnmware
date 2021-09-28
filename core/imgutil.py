# nnmware(c)2012-2020

from __future__ import unicode_literals
import os
import fnmatch
import shutil
from urllib.parse import urljoin
from PIL import Image, ImageOps

from django.conf import settings

from nnmware.core.utils import setting
from nnmware.core.file import get_path_from_url


TMB_MASKS = ['%s_t*%s', '%s_aspect*%s', '%s_wm*%s']


def _get_thumbnail_path(path, width=None, height=None, aspect=None, watermark=None):
    """ create thumbnail path from path and required width and/or height.
        thumbnail file name is constructed like this:
            <basename>_t_[w<width>][_h<height>].<extension>
        or if aspect - <basename>_aspect_[w<width>][_h<height>].<extension>
     """

    # one of width/height is required
    assert (width is not None) or (height is not None) or (watermark is not None)

    basedir = os.path.dirname(path) + '/'
    base, ext = os.path.splitext(os.path.basename(path))

    # make thumbnail filename
    if aspect:
        th_name = base + '_aspect'
    elif watermark:
        th_name = base + '_wm'
    else:
        th_name = base + '_t'
    if (width is not None) and (height is not None):
        th_name += '_w%d_h%d' % (width, height)
    elif width is not None:
        th_name += '%d' % width  # for compatibility with admin
    elif height is not None:
        th_name += '_h%d' % height
    th_name += ext
    return urljoin(basedir, th_name)


def _has_thumbnail(photo_url, width=None, height=None,
                   root=settings.MEDIA_ROOT, url_root=settings.MEDIA_URL, aspect=None, watermark=None):
    # one of width/height is required
    assert (width is not None) or (height is not None) or (watermark is not None)

    return os.path.isfile(get_path_from_url(_get_thumbnail_path(photo_url,
                                                                width, height, aspect, watermark), root, url_root))


def make_thumbnail(photo_url, width=None, height=None, aspect=None,
                   root=settings.MEDIA_ROOT, url_root=settings.MEDIA_URL):
    """ create thumbnail """

    # one of width/height is required
    assert (width is not None) or (height is not None)
    size = None
    if not photo_url:
        return None
    th_url = _get_thumbnail_path(photo_url, width, height, aspect)
    th_path = get_path_from_url(th_url, root, url_root)
    photo_path = get_path_from_url(photo_url, root, url_root)

    if _has_thumbnail(photo_url, width, height, root, url_root, aspect):
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

    # noinspection PyBroadException
    try:
        img = Image.open(photo_path).copy()
        if aspect:
            img = ImageOps.fit(img, size, Image.ANTIALIAS, 0.5)
        img.thumbnail(size, Image.ANTIALIAS)
        img.save(th_path, quality=setting('THUMBNAIL_QUALITY', 85))
    except:
        return photo_url
    return th_url


def remove_thumbnails(pic_url, root=settings.MEDIA_ROOT, url_root=settings.MEDIA_URL):
    if not pic_url:
        return  # empty url
    file_name = get_path_from_url(pic_url, root, url_root)
    base, ext = os.path.splitext(os.path.basename(file_name))
    basedir = os.path.dirname(file_name)
    for item in TMB_MASKS:
        # noinspection PyBroadException
        try:
            for f in fnmatch.filter(os.listdir(str(basedir)), item % (base, ext)):
                path = os.path.join(basedir, f)
                try:
                    os.remove(path)
                except OSError as oserr:
                    pass
        except:
            pass


def remove_file(f_url, root=settings.MEDIA_ROOT, url_root=settings.MEDIA_URL):
    if not f_url:
        return  # empty url
    file_name = get_path_from_url(f_url, root, url_root)
    # noinspection PyBroadException
    try:
        os.remove(file_name)
    except:
        pass


def resize_image(img_url, width=400, height=400, root=settings.MEDIA_ROOT, url_root=settings.MEDIA_URL):
    file_name = get_path_from_url(img_url, root, url_root)
    im = Image.open(file_name)
    if im.size[0] > width or im.size[1] > height:
        im.thumbnail((width, height), Image.ANTIALIAS)
    im.save(file_name, "JPEG", quality=88)


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


def get_image_size(photo_url, root=settings.MEDIA_ROOT, url_root=settings.MEDIA_URL):
    """ returns image size.
    """
    path = get_path_from_url(photo_url, root, url_root)
    # noinspection PyBroadException
    try:
        size = Image.open(path).size
    except:
        # this goes to webserver error log
        return None, None
    return size


##################################################
# FILE HELPERS ##

def _rename(old_name, new_name):
    """ rename image old_name -> name """
    try:
        shutil.move(os.path.join(settings.MEDIA_ROOT, old_name), os.path.join(settings.MEDIA_ROOT, new_name))
        return new_name
    except IOError as ioerr:
        return old_name


def fit(image, size):
    # Resize Image not more then SIZEpx width.. or Enlarge Image is smaller then SIZE
    wpercent = (size / float(image.size[0]))
    hsize = int((float(image.size[1]) * float(wpercent)))
    image = image.resize((size, hsize), Image.ANTIALIAS)
    return image


def aspect_ratio(image, w, h):
    # Function for make Aspect Ratio of Image(i.e 16:9)
    image_width = image.size[0]
    image_height = image.size[1]
    new_image_height = int((image_width / w) * h)
    top_crop = int((image_height - new_image_height) / 2)
    bottom_crop = image_height - top_crop
    box = (0, top_crop, image_width, bottom_crop)
    image = image.crop(box)
    return image


def get_thumbnail_path(url, size):
    url_t = make_thumbnail(url, width=size)
    return get_path_from_url(url_t)


def make_watermark(photo_url, align='lt', root=settings.MEDIA_ROOT, url_root=settings.MEDIA_URL):
    """ create watermark """
    photo_path = get_path_from_url(photo_url, root, url_root)
    watermark_path = settings.WATERMARK
    wm_url = _get_thumbnail_path(photo_url, watermark=1)
    wm_path = get_path_from_url(wm_url, root, url_root)
    if _has_thumbnail(photo_url, watermark=1):
        # thumbnail already exists
        if not (os.path.getmtime(photo_path) > os.path.getmtime(wm_path)) and \
                not (os.path.getmtime(watermark_path) > os.path.getmtime(wm_path)):
            # if photo mtime is newer than thumbnail recreate thumbnail
            return wm_url
    try:
        base_im = Image.open(photo_path)
        logo_im = Image.open(watermark_path)  # transparent image
    except IOError as ioerr:
        return None
    if align == 'center':
        base_im.paste(logo_im, ((base_im.size[0] - logo_im.size[0]) / 2, (base_im.size[1] - logo_im.size[1]) / 2),
                      logo_im)
    else:
        base_im.paste(logo_im, (base_im.size[0] - logo_im.size[0], base_im.size[1] - logo_im.size[1]), logo_im)
    base_im.convert('RGB')
    base_im.save(wm_path, "JPEG")
    return wm_url
