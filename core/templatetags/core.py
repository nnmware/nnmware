from datetime import datetime, timedelta
from django import template
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum
from nnmware.apps.video.models import Video
from nnmware.core.models import Tag


register = template.Library()

@register.assignment_tag
def video_links():
    return Video.objects.all()[:4]


@register.assignment_tag
def tag_links():
    # Return most popular 10 Tags
    return Tag.objects.annotate(video_count=Count('video')).order_by('-video_count')[:10]

@register.simple_tag
def video_views():
    return Video.objects.aggregate(Sum('viewcount'))['viewcount__sum']

def do_get_tree_path(parser, token):
#    name, link = content_object.get_full_path()
    result = ''
    for name, link in token.get_full_path():
        result += '<a href="%s">%s</a>' % name, link
    return result

@register.filter
def multiply(value, times):
    return value*times

@register.filter("inline_truncate")
def inline_truncate(value, size):
    """Truncates a string to the given size placing the ellipsis at the middle of the string"""
    new = ''
    for w in value.split():
        if len(w) > size > 3:
            start = (size - 3) / 2
            end = (size - 3) - start
            new += ' ' + w[0:start] + '...' + w[-end:]
        else:
            new += ' ' + w[0:size]
    return new

inline_truncate.is_safe = True


@register.filter
def inline_word(value, size):
    """Append spaces in long word"""
    new = ''
    for w in value.split():
        if len(w) > size:
            while len(w) > size:
                new += w[:size]
                w = w[size:]
            new += ' ' + w
        else:
            new += ' ' + w
    return new

inline_word.is_safe = True


@register.filter("latestdates")
def latestdates(date):
    if datetime.now() - date < timedelta(hours=24):
        return 'red'
    else:
        return 'normal'

@register.filter("short_urlize")
def short_urlize(url):
    if 'http://www.' in url:
        url_short = url[11:-1]
    elif 'http://' in url:
        url_short = url[7:-1]
    else:
        url_short = url
    result = "<a href='%s' target='_blank' >%s</a>" % (url,url_short)
    return mark_safe(result)


register.tag('get_tree_path', do_get_tree_path)

@register.inclusion_tag("paginator.html", takes_context=True)
def paginator(context, adjacent_pages=2):
    """
    To be used in conjunction with the object_list generic view.

    Adds pagination context variables for use in displaying first, adjacent and
    last page links in addition to those created by the object_list generic
    view.
    """
    page_numbers = [n for n in \
                    range(context["paginator"].num_pages - adjacent_pages,
                    context["paginator"].num_pages + adjacent_pages + 1) \
                    if n > 0 and n <= context["paginator"].num_pages]
    return {
        "hits": context["hits"],
        "results_per_page": context["results_per_page"],
        "page": context["page"],
        "pages": context["pages"],
        "page_numbers": page_numbers,
        "next": context["next"],
        "previous": context["previous"],
        "has_next": context["has_next"],
        "has_previous": context["has_previous"],
        "show_first": 1 not in page_numbers,
        "show_last": context["pages"] not in page_numbers,
        }

