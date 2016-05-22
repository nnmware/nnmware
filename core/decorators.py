# nnmware(c)2012-2016

from __future__ import unicode_literals
from functools import wraps
from urllib.parse import urljoin

from django.conf import settings
from django.http import HttpResponseRedirect

from nnmware.core.utils import setting


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
        except AttributeError as aerr:
            return func(manager, *args, **kwargs).fetch_generic_relations()
    return wrapped


def ssl_required(view_func):
    def _checkssl(request, *args, **kwargs):
        if not request.is_secure() and not settings.DEBUG and not setting('NOHTTPS', True):
            if hasattr(settings, 'SSL_DOMAIN'):
                url_str = urljoin(
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
