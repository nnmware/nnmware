from django.template import Library
from django.conf import settings

register = Library()

if settings.DEBUG:
    @register.inclusion_tag('core/debug.html')
    def site_debug():
        import re
        from django.db import connection

        queries = connection.queries
        query_time = 0
        query_count = 0
        for query in queries:
            query_time += float(query['time'])
            query_count += int(1)
        return {
            'query_time': query_time,
            'query_count': query_count}
else:
    @register.simple_tag
    def site_debug():
        return ''
