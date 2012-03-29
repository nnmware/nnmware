import re

from django.template import Library, Context, loader
from django.core.urlresolvers import reverse

try:
    from django.utils.safestring import mark_safe
except ImportError:
    mark_safe = lambda x: x

register = Library()


@register.filter
def datelinks(value):
    """
    This filter formats date as "day.month.year" and sets links to
    day/month/year-based archives.

    For correct work there must be defined urls with names:
        - day_archive
        - month_archive
        - year_archive
    """
    return get_links(value.strftime('%d'), value.strftime('%m'), value.year)


@register.filter
def datelinks_by_string(value):
    """
    This filter creates from date formatted as "day.month.year" string with
    links to day/month/year-based archives.

    For correct work there must be defined urls with names:
        - day_archive
        - month_archive
        - year_archive
    """
    r = r'^(?P<day>\d{2})\.(?P<month>\d{2})\.(?P<year>\d{4})$'
    try:
        day, month, year = re.match(r, value).groups()
    except AttributeError:
        return value
    return get_links(day, month, year)


def get_links(day, month, year):
    return mark_safe(loader.render_to_string('core/datelinks.html',
            {'year': year, 'month': month, 'day': day}
    ))


@register.filter
def get_month(date):
    return date.strftime('%m')


@register.filter
def get_day(date):
    return date.strftime('%d')
