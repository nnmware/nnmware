from datetime import datetime, timedelta
from django import template
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum
from nnmware.apps.video.models import Video
from nnmware.core.models import Tag


register = template.Library()

def video_links(context, mode='random'):
    user= context["user"]
    try:
        category = context['category_panel']
    except KeyError:
        category = None
    videos = Video.objects.filter(publish_date__gte=datetime.now()-timedelta(days=1))
    result = videos
    if user.is_authenticated():
        result = result.exclude(users_viewed = user)
    if category is not None:
        result = result.filter(tags = category)
    if mode == 'popular':
        result = list(result.order_by('viewcount')[:2])
    else:
        result = list(result.order_by('?')[:2])
    if len(result) < 2:
        result.extend(list(videos.order_by('?')))
    if len(result) < 2:
        result.extend(list(Video.objects.order_by('?')))
    return result[:2]

@register.assignment_tag(takes_context=True)
def video_popular_links(context):
    return video_links(context, mode='popular')

@register.assignment_tag(takes_context=True)
def video_other_links(context):
    return video_links(context)

@register.assignment_tag
def tag_links():
    # Return most popular 10 Tags
    return Tag.objects.annotate(video_count=Count('video')).order_by('-video_count')[:10]

@register.assignment_tag
def tags_step2():
    # Return most popular 10 Tags
    return Tag.objects.annotate(video_count=Count('video')).order_by('-video_count')[:9]

@register.assignment_tag(takes_context=True)
def users_step2(context):
    request = context['request']
    # Return most popular 6 users
    return User.objects.exclude(username=request.user.username).annotate(video_count=Count('video')).order_by('-video_count')[:6]


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

LEADING_PAGE_RANGE_DISPLAYED = TRAILING_PAGE_RANGE_DISPLAYED = 10
LEADING_PAGE_RANGE = TRAILING_PAGE_RANGE = 8
NUM_PAGES_OUTSIDE_RANGE = 2
ADJACENT_PAGES = 4

@register.assignment_tag(takes_context=True)
def paginator(context):
    """
    Paginator for CBV and paginate_by
    """
    num_pages= context["paginator"].num_pages
    curr_page_num = context["page_obj"].number
    in_leading_range = in_trailing_range = False
    pages_outside_leading_range = pages_outside_trailing_range = range(0)

    if num_pages <= LEADING_PAGE_RANGE_DISPLAYED:
        in_leading_range = in_trailing_range = True
        page_numbers = [n for n in range(1, num_pages + 1) if 0 < n <= num_pages]
    elif curr_page_num <= LEADING_PAGE_RANGE:
        in_leading_range = True
        page_numbers = [n for n in range(1, LEADING_PAGE_RANGE_DISPLAYED + 1) if 0 < n <= num_pages]
        pages_outside_leading_range = [n + num_pages for n in range(0, -NUM_PAGES_OUTSIDE_RANGE, -1)]
    elif curr_page_num > (num_pages - TRAILING_PAGE_RANGE):
        in_trailing_range = True
        page_numbers = [n for n in range(num_pages - TRAILING_PAGE_RANGE_DISPLAYED + 1, num_pages + 1) if 0 < n <= num_pages]
        pages_outside_trailing_range = [n + 1 for n in range(0, NUM_PAGES_OUTSIDE_RANGE)]
    else:
        page_numbers = [n for n in range(curr_page_num - ADJACENT_PAGES, curr_page_num + ADJACENT_PAGES + 1) if 0 < n <= num_pages]
        pages_outside_leading_range = [n + num_pages for n in range(0, -NUM_PAGES_OUTSIDE_RANGE, -1)]
        pages_outside_trailing_range = [n + 1 for n in range(0, NUM_PAGES_OUTSIDE_RANGE)]
    getvars = context['request'].GET.copy()
    if 'page' in getvars:
        del getvars['page']
    if len(getvars.keys()) > 0:
        new_getvars = "&%s" % getvars.urlencode()
    else:
        new_getvars = ''
    return {
        "getvars":new_getvars,
        "page_numbers": page_numbers,
        "in_leading_range" : in_leading_range,
        "in_trailing_range" : in_trailing_range,
        "pages_outside_leading_range": pages_outside_leading_range,
        "pages_outside_trailing_range": pages_outside_trailing_range
        }

@register.filter
def no_end_slash(value):
    if value[-1:] == '/':
        return value[:-1]
    else:
        return value
