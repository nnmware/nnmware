from django.contrib import messages
from nnmware.core.utils import get_message_dict
from django.utils import simplejson

from threading import local

_thread_locals = local()


def get_request():
    return getattr(_thread_locals, 'request', None)


class ThreadLocalsMiddleware(object):
    """Middleware that saves request in thread local storage"""

    def process_request(self, request):
        _thread_locals.request = request


def get_page(self):
    """
    A function which will be monkeypatched onto the request to get the current
    integer representing the current page.
    """
    try:
        return int(self.REQUEST['page'])
    except (KeyError, ValueError, TypeError):
        return 1


class PaginationMiddleware(object):
    """
    Inserts a variable representing the current page onto the request object if
    it exists in either **GET** or **POST** portions of the request.
    """

    def process_request(self, request):
        request.__class__.page = property(get_page)


class AjaxMessagingMiddleware(object):
    def process_response(self, request, response):
        if request.is_ajax():
            if response['Content-Type'] in ["application/javascript", "application/json"]:
                try:
                    content = simplejson.loads(response.content)
                except ValueError:
                    return response
                django_messages = []
                for message in messages.get_messages(request):
                    django_messages.append({
                        "level": message.level,
                        "message": message.message,
                        "extra_tags": message.tags,
                        })
                content['core_messages'] = django_messages
                response.content = simplejson.dumps(content)
        return response
