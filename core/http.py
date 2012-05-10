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


def get_object_or_none(klass, *args, **kwargs):
    """
    Uses get() to return an object or None if the object does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Note: Like with get(), an MultipleObjectsReturned will be
    raised if more than one
    object is found.
    """
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None


def handle_uploads(request, path, keys):
    saved = []
    upload_dir = os.path.join(settings.MEDIA_ROOT, path)
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    for key in keys:
        if key in request.FILES:
            upload = request.FILES[key]
            while os.path.exists(os.path.join(upload_dir, upload.name)):
                upload.name = '_' + upload.name
            dest = open(os.path.join(upload_dir, upload.name), 'wb')
            for chunk in upload.chunks():
                dest.write(chunk)
            dest.close()
            saved.append((key, os.path.join(upload_dir, upload.name)))
            # returns [(key1, path1), (key2, path2), ...]
    return saved
