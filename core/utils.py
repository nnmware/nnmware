# -*- coding: utf-8 -*-

import hashlib
import re
import string
import unicodedata
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import os
import random
import sys
import types
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import smart_text
from django.utils.timezone import now
from nnmware.core import oembed
import unidecode
from BeautifulSoup import BeautifulSoup


VALID = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-0123456789'


def make_key(name):
    salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
    if isinstance(name, unicode):
        name = name.encode('utf-8')
    activation_key = hashlib.sha1(salt + name).hexdigest()
    return activation_key


def convert_to_date(d):
    return datetime.strptime(d, "%d.%m.%Y")


def get_date_directory():
    return now().strftime("%Y/%m/%d/%H/%M/%S")


def get_oembed_end_point(link=''):
    if link.find('youtube.com') != -1:
        return oembed.OEmbedEndpoint('http://www.youtube.com/oembed', ['http://*.youtube.com/*'])
    elif link.find('vimeo.com') != -1:
        return oembed.OEmbedEndpoint('http://vimeo.com/api/oembed.json', ['http://vimeo.com/*'])
    else:
        return None


def get_video_provider_from_link(link):
    if link.find('youtube.com') != -1:
        return "youtube.com"
    elif link.find('vimeo.com') != -1:
        return "vimeo.com"
    else:
        return None


def update_video_size(html, w, h):
    # Change parameters in Iframe src of EOMBED
    new_width = 'width="' + str(w) + '"'
    new_height = 'height="' + str(h) + '"'
    patern1 = r'width="\d+"'
    patern2 = r'height="\d+"'
    html = re.sub(patern1, new_width, html)
    html = re.sub(patern2, new_height, html)
    return html


def slug_tag(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = unicode(unidecode.unidecode(BeautifulSoup(value).contents[0]))
    #    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = re.sub('[^\w\s-]', '', value).strip().title()
    return value


def tags_normalize(s):
    return map(lambda x: slug_tag(x), s.split(','))


def gen_shortcut(num):
    """
    Generates a short URL for any URL on Django site.  It is intended to
    make long URLs short, a la TinyURL.com.
    """
    short = ''
    if num:
        num, remainder = divmod(num - 1, len(VALID))
        short += VALID[remainder]
    return short


def slugify(s):
    """
    Replacement for Django's slugify which allows unicode chars in
    slugs, for URLs in Chinese, Russian, etc.
    Adopted from https://github.com/mozilla/unicode-slugify/
    """
    chars = []
    for char in smart_text(s):
        cat = unicodedata.category(char)[0]
        if cat in "LN" or char in "-_~":
            chars.append(char)
        elif cat == "Z":
            chars.append(" ")
    return re.sub("[-\s]+", "-", "".join(chars).strip()).lower()


def can_loop_over(maybe):
    """Test value to see if it is list like"""
    try:
        iter(maybe)
    except:
        return 0
    else:
        return 1


def cross_list(sequences):
    """
    Code taken from the Python cookbook v.2 (19.9 - Looping through the cross-product of multiple iterators)
    This is used to create all the variations associated with an product
    """
    result = [[]]
    for seq in sequences:
        result = [sublist + [item] for sublist in result for item in seq]
    return result


def is_scalar(maybe):
    """Test to see value is a string, an int, or some other scalar type"""
    return is_string_like(maybe) or not can_loop_over(maybe)


def flatten_list(sequence, scalarp=is_scalar, result=None):
    """flatten out a list by putting sublist entries in the main list"""
    if result is None:
        result = []

    for item in sequence:
        if scalarp(item):
            result.append(item)
        else:
            flatten_list(item, scalarp, result)


def flatten(sequence, scalarp=is_scalar):
    """flatten out a list by putting sublist entries in the main list"""
    for item in sequence:
        if scalarp(item):
            yield item
        else:
            for subitem in flatten(item, scalarp):
                yield subitem


def get_flat_list(sequence):
    """flatten out a list and return the flat list"""
    flat = []
    flatten_list(sequence, result=flat)
    return flat


def is_list_or_tuple(maybe):
    return isinstance(maybe, (types.TupleType, types.ListType))


def is_string_like(maybe):
    """Test value to see if it acts like a string"""
    try:
        maybe + ""
    except TypeError:
        return 0
    else:
        return 1


def load_module(module):
    """Load a named python module."""
    try:
        module = sys.modules[module]
    except KeyError:
        __import__(module)
        module = sys.modules[module]
    return module


_MODULES = []


def load_once(key, module):
    if key not in _MODULES:
        load_module(module)
        _MODULES.append(key)


def normalize_dir(dir_name):
    if not dir_name.startswith('./'):
        dir_name = url_join('.', dir_name)
    if dir_name.endswith("/"):
        dir_name = dir_name[:-1]
    return dir_name


def request_is_secure(request):
    if request.is_secure():
        return True
    if 'HTTP_X_FORWARDED_SSL' in request.META:
        return request.META['HTTP_X_FORWARDED_SSL'] == 'on'

    return False


def trunc_decimal(val, places):
    roundfmt = "0."
    if places > 1:
        zeros = "0" * (places - 1)
        roundfmt += zeros
    if places > 0:
        roundfmt += "1"
    if type(val) != Decimal:
        try:
            val = Decimal(val)
        except InvalidOperation:
            return val
    return val.quantize(Decimal(roundfmt), ROUND_HALF_UP)


def url_join(*args):
    """Join any arbitrary strings into a forward-slash delimited string.
    Do not strip leading / from first element, nor trailing / from last element.

    This function can take lists as arguments, flattening them appropriately.

    example:
    url_join('one','two',['three','four'],'five') => 'one/two/three/four/five'
    """
    if not len(args):
        return ""

    args = get_flat_list(args)

    if len(args) == 1:
        return str(args[0])

    else:
        args = [str(arg).replace("\\", "/") for arg in args]

        work = [args[0]]
        for arg in args[1:]:
            if arg.startswith("/"):
                work.append(arg[1:])
            else:
                work.append(arg)

        joined = reduce(os.path.join, work)

    return joined.replace("\\", "/")


def get_message_dict(message):
    """
    Returns message dictionary. If `persistent_messages` used includes
    additional attributes, such as `id`, for special actions with messages (marking read)
    """
    message_dict = {
        'level': message.level,
        'text': message.message,
        'tags': message.tags,
    }
    return message_dict


def date_range(from_date, to_date):
    result = [from_date]
    d = from_date
    while d < to_date:
        d = d + timedelta(days=1)
        result.append(d)
    return result


def daterange(start_date, end_date):
    for n in range((end_date - start_date).days):
        yield start_date + timedelta(n)


def send_template_mail(subject, body, mail_dict, recipients):
    try:
        subject = render_to_string(subject, mail_dict)
        subject = ''.join(subject.splitlines())
        body = render_to_string(body, mail_dict)
        send_mail(subject=subject, message=body, from_email=settings.EMAIL_HOST_USER, recipient_list=recipients)
    except:
        pass


def setting(name, default=None):
    """Return setting value for given name or default value."""
    return getattr(settings, name, default)


def tuplify(x):
    return x, x  # str(x) if needed

current_year = now().year


def random_pw(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


# def video_replace(txt):
#     answer = txt
#     urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', txt)
#     for url in urls:
#         if 1>0: #try:
#             if url.find('youtu.be') != -1:
#                 url = url.replace('youtu.be/', 'www.youtube.com/watch?v=')
#                 consumer = oembed.OEmbedConsumer()
#                 endpoint = get_oembed_end_point(url)
#                 consumer.add_endpoint(endpoint)
#                 response = consumer.embed(url)
#                 result = response.get_data()
#                 video_code = update_video_size(result['html'], 500, 280)
#                 answer.replace(url, video_code)
#         # except:
#         #     pass
#     return answer


def query_user_pk_distinct(query):
    result = query.values_list('pk', flat=True).distinct()
    users = get_user_model().objects.filter(pk__in=result)
    return users
