# -*- encoding: utf-8 -*-

""" image related filters """

##################################################
## DEPENDENCIES ##

from django.conf import settings
from nnmware.apps.userprofile.models import Profile
from nnmware.core.imgutil import make_thumbnail, get_image_size
import os
import time
from django.template import Library, Node, Template, TemplateSyntaxError, Variable
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

try:
    from PIL import Image
except ImportError:
    import Image

register = Library()

DEFAULT_AVATAR = os.path.join(settings.MEDIA_ROOT, settings.DEFAULT_AVATAR)


##################################################
## FILTERS ##


def thumbnail(url, args=''):
    """ Returns thumbnail URL and create it if not already exists.

.. note:: requires PIL_,
    if PIL_ is not found or thumbnail can not be created returns original URL.

.. _PIL: http://www.pythonware.com/products/pil/

Usage::

    {{ url|thumbnail:"width=10,height=20" }}
    {{ url|thumbnail:"width=10" }}
    {{ url|thumbnail:"height=20" }}

Parameters:

width
    requested image width

height
    requested image height

Image is **proportionally** resized to dimension which is no greather than ``width x height``.

Thumbnail file is saved in the same location as the original image
and his name is constructed like this::

    %(dirname)s/%(basename)s_t[_w%(width)d][_h%(height)d].%(extension)s

or if only a width is requested (to be compatibile with admin interface)::

    %(dirname)s/%(basename)s_t%(width)d.%(extension)s

"""

    kwargs = {}
    if args:
        if ',' not in args:
            # ensure at least one ','
            args += ','
        for arg in args.split(','):
            arg = arg.strip()
            if arg == '':
                continue
            kw, val = arg.split('=', 1)
            kw = kw.lower().encode('ascii')
            try:
                val = int(val)  # convert all ints
            except ValueError:
                raise TemplateSyntaxError, "thumbnail filter: argument %r is invalid integer (%r)" % (kw, val)
            kwargs[kw] = val

    if ('width' not in kwargs) and ('height' not in kwargs):
        raise TemplateSyntaxError, "thumbnail filter requires arguments (width and/or height)"

    ret = make_thumbnail(url, **kwargs)
    if ret is None:
        ret = url

    if not ret.startswith(settings.MEDIA_URL):
        ret = settings.MEDIA_URL + ret

    return ret

#
register.filter('thumbnail', thumbnail)

class ResizedThumbnailNode(Node):
    def __init__(self, size, username=None):
        try:
            self.size = int(size)
        except:
            self.size = Variable(size)
        if username:
            self.user = Variable(username)
        else:
            self.user = Variable("user")

    def render(self, context):
        # If size is not an int, then it's a Variable, so try to resolve it.
        if not isinstance(self.size, int):
            self.size = int(self.size.resolve(context))

        try:
            user = self.user.resolve(context)
            avatar = Profile.objects.get(user=user).avatar
            avatar_path = avatar.path
        except:
            avatar_path = DEFAULT_AVATAR
            url = avatar_path.replace(settings.MEDIA_ROOT, settings.MEDIA_URL)

        ret = make_thumbnail(avatar_path, width=self.size)
        ret = ret.replace(settings.MEDIA_ROOT, settings.MEDIA_URL)

        if ret is None:
            ret = avatar_path

        if not ret.startswith(settings.MEDIA_URL):
            ret = settings.MEDIA_URL + ret

        return ret


@register.tag
def avatar(parser, token):
    bits = token.contents.split()
    username = None
    if len(bits) > 3:
        raise TemplateSyntaxError, _(u"You have to provide only the size as \
            an integer (both sides will be equal) and optionally, the \
            username.")
    elif len(bits) == 3:
        username = bits[2]
    elif len(bits) < 2:
        bits.append("96")
    return ResizedThumbnailNode(bits[1], username)




def image_width(url):
    """ Returns image width.

Usage:
    {{ url|image_width }}
"""

    width, height = get_image_size(url)
    return width

#

register.filter('image_width', image_width)


def image_height(url):
    """ Returns image height.

Usage:
    {{ url|image_width }}
"""

    width, height = get_image_size(url)
    return height

#

register.filter('image_height', image_height)

