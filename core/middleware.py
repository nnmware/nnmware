import json
from django.conf import settings
from django.contrib import messages
from django.utils.timezone import now
from nnmware.core.http import get_session_from_request


class AjaxMessagingMiddleware(object):
    def process_response(self, request, response):
        if request.is_ajax():
            if response['Content-Type'] in ["application/javascript", "application/json"]:
                try:
                    content = json.loads(response.content)
                except ValueError:
                    return response
                django_messages = []
                for message in messages.get_messages(request):
                    django_messages.append(dict(level=message.level, message=message.message, extra_tags=message.tags))
                content['core_messages'] = django_messages
                response.content = json.dumps(content)
        return response


UNTRACKED_USER_AGENT = [
    "Teoma", "alexa", "froogle", "Gigabot", "inktomi", "looksmart", "URL_Spider_SQL", "Firefly",
    "NationalDirectory", "Ask Jeeves", "TECNOSEEK", "InfoSeek", "WebFindBot", "girafabot", "crawler",
    "www.galaxy.com", "Googlebot", "Googlebot/2.1", "Google", "Webmaster", "Scooter", "James Bond",
    "Slurp", "msnbot", "appie", "FAST", "WebBug", "Spade", "ZyBorg", "rabaz", "Baiduspider",
    "Feedfetcher-Google", "TechnoratiSnoop", "Rankivabot", "Mediapartners-Google", "Sogou web spider",
    "WebAlta Crawler", "MJ12bot", "Yandex/", "YandexBot", "YaDirectBot", "StackRambler", "DotBot", "dotbot",
    "AhrefsBot", "Mail.RU_Bot", "YandexDirect", "Twitterbot", "PaperLiBot", "bingbot", "Ezooms", 'SiteExplorer'
]


class VisitorHitMiddleware(object):
    def process_request(self, request):
        if request.is_ajax():
            return
        if request.path.startswith(settings.ADMIN_SYSTEM_PREFIX):
            return
            # see if the user agent is not supposed to be tracked
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
        for ua in UNTRACKED_USER_AGENT:
            # if the keyword is found in the user agent, stop tracking
            if user_agent.find(ua) != -1:
                return
        from nnmware.core.models import VisitorHit

        v = VisitorHit()
        if request.user.is_authenticated():
            v.user = request.user
        v.user_agent = user_agent
        v.ip_address = request.META.get('REMOTE_ADDR', '')
        v.session_key = get_session_from_request(request)
        v.secure = request.is_secure()
        v.referer = request.META.get('HTTP_REFERER', '')
        v.hostname = request.META.get('REMOTE_HOST', '')[:100]
        v.url = request.get_full_path()
        v.date = now()
        v.save()
