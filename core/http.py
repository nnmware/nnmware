import os
from django.conf import settings
from django.core.serializers import serialize
from django.shortcuts import _get_queryset
from django.http import Http404, HttpResponse
from django.utils.functional import Promise
from django.utils.encoding import force_unicode
import json


def response_mimetype(request):
    if "application/json" in request.META['HTTP_ACCEPT']:
        return "application/json"
    else:
        return "text/plain"


class LazyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_unicode(obj)
        return obj


class JSONResponse(HttpResponse):
    """
    A simple subclass of ``HttpResponse`` which makes serializing to JSON easy.
    """

    def __init__(self, object, is_iterable=True):
        if is_iterable:
            content = serialize('json', object)
        else:
            content = json.dumps(object, cls=LazyEncoder)
        super(JSONResponse, self).__init__(content,
            mimetype='application/json')


class XMLResponse(HttpResponse):
    """
    A simple subclass of ``HttpResponse`` which makes serializing to XML easy.
    """

    def __init__(self, object, is_iterable=True):
        if is_iterable:
            content = serialize('xml', object)
        else:
            content = object
        super(XMLResponse, self).__init__(content, mimetype='application/xml')


def redirect(request):
    """Get appropriate url for redirect"""
    if request.POST.get('next'):
        return request.POST.get('next')
    else:
        if request.GET.get('next'):
            return request.GET.get('next')
        else:
            return request.META.get('HTTP_REFERER', '/')

