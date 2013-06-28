# -*- coding: utf-8 -*-

from functools import wraps
import urlparse

from django.conf import settings
from django.http import HttpResponseRedirect

from nnmware.core.http import JSONResponse


def stream(func):
    """
    Stream decorator to be applied to methods of an ``ActionManager`` subclass

    Syntax::

        from nnmware.core.decorators import stream
        from nnmware.core.managers import ActionManager

        class MyManager(ActionManager):
            @stream
            def foobar(self, ...):
                ...

    """
    @wraps(func)
    def wrapped(manager, *args, **kwargs):
        offset, limit = kwargs.pop('_offset', None), kwargs.pop('_limit', None)
        try:
            return func(manager, *args, **kwargs)[offset:limit]\
                .fetch_generic_relations()
        except AttributeError:
            return func(manager, *args, **kwargs).fetch_generic_relations()
    return wrapped


def ajax_request(func):
    """
    Checks request.method is POST. Return error in JSON in other case.

    If view returned dict, returns JSONResponse with this dict as content.
    """

    def wrapper(request, *args, **kwargs):
        if request.method == 'POST':
            response = func(request, *args, **kwargs)
        else:
            response = {'error': {'type': 403,
                        'message': 'Accepts only POST request'}}
        if isinstance(response, dict):
            return JSONResponse(response)
        else:
            return response

    return wrapper


def ssl_required(view_func):
    def _checkssl(request, *args, **kwargs):
        if not request.is_secure() and not settings.DEBUG and not settings.NOHTTPS:
            if hasattr(settings, 'SSL_DOMAIN'):
                url_str = urlparse.urljoin(
                    settings.SSL_DOMAIN,
                    request.get_full_path()
                )
            else:
                url_str = request.build_absolute_uri()
            url_str = url_str.replace('http://', 'https://')
            return HttpResponseRedirect(url_str)

        return view_func(request, *args, **kwargs)
    return _checkssl


def ssl_not_required(view_func):
    def _checkssl(request, *args, **kwargs):
        if request.is_secure():
            url_str = request.build_absolute_uri()
            url_str = url_str.replace('https://', 'http://')
            return HttpResponseRedirect(url_str)
        return view_func(request, *args, **kwargs)
    return _checkssl
