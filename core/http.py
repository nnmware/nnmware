# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

from django.utils.functional import Promise
from django.utils.encoding import force_text


# def response_mimetype(request):
#     if "application/json" in request.META['HTTP_ACCEPT']:
#         return "application/json"
#     else:
#         return "text/plain"
#
#
class LazyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return obj


def redirect(request):
    """Get appropriate url for redirect"""
    if request.POST.get('next'):
        return request.POST.get('next')
    else:
        if request.GET.get('next'):
            return request.GET.get('next')
        else:
            return request.META.get('HTTP_REFERER', '/')


def get_session_from_request(request):
    if hasattr(request, 'session') and request.session.session_key:
        # use the current session key if we can
        session_key = request.session.session_key
    else:
        # otherwise just fake a session key
        session_key = '%s:%s' % (request.META.get('REMOTE_ADDR', ''), request.META.get('HTTP_USER_AGENT', '')[:255])
        session_key = session_key[:40]
    return session_key

