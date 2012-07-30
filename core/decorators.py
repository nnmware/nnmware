
from functools import wraps
import urlparse

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.utils.importlib import import_module

from nnmware.apps.social.backends import get_backend
from nnmware.apps.social.utils import log, backend_setting
from nnmware.core.utils import setting
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
        if not request.is_secure() and not settings.DEBUG:
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


LOGIN_ERROR_URL = setting('LOGIN_ERROR_URL', setting('LOGIN_URL'))
PROCESS_EXCEPTIONS = setting('SOCIAL_AUTH_PROCESS_EXCEPTIONS',
    'social_auth.utils.log_exceptions_to_messages')


def dsa_view(redirect_name=None):
    """Decorate djangos-social-auth views. Will check and retrieve backend
    or return HttpResponseServerError if backend is not found.

        redirect_name parameter is used to build redirect URL used by backend.
    """
    def dec(func):
        @wraps(func)
        def wrapper(request, backend, *args, **kwargs):
            if redirect_name:
                redirect = reverse(redirect_name, args=(backend,))
            else:
                redirect = request.path
            backend = get_backend(backend, request, redirect)

            if not backend:
                return HttpResponseServerError('Incorrect authentication ' +\
                                               'service')

            RAISE_EXCEPTIONS = backend_setting(backend, 'SOCIAL_AUTH_RAISE_EXCEPTIONS', setting('DEBUG'))
            try:
                return func(request, backend, *args, **kwargs)
            except Exception, e:  # some error ocurred
                if RAISE_EXCEPTIONS:
                    raise
                log('error', unicode(e), exc_info=True, extra={
                    'request': request
                })

                mod, func_name = PROCESS_EXCEPTIONS.rsplit('.', 1)
                try:
                    process = getattr(import_module(mod), func_name,
                        lambda *args: None)
                except ImportError:
                    pass
                else:
                    process(request, backend, e)

                url = backend_setting(backend, 'SOCIAL_AUTH_BACKEND_ERROR_URL',
                    LOGIN_ERROR_URL)
                return HttpResponseRedirect(url)
        return wrapper
    return dec
