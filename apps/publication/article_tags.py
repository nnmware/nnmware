# nnmware(c)2012-2020

from datetime import datetime

from django import template
from django.core.cache import cache

from nnmware.apps.publication.models import Publication


register = template.Library()


class GetPublicationsNode(template.Node):
    """
    Retrieves a set of article objects.

    Usage::

        {% get_articles 5 as varname %}

        {% get_articles 5 as varname asc %}

        {% get_articles 1 to 5 as varname %}

        {% get_articles 1 to 5 as varname asc %}
    """

    def __init__(self, varname, count=None, start=None, end=None, order='desc'):
        self.count = count
        self.start = start
        self.end = end
        self.order = order
        self.varname = varname.strip()

    def render(self, context):
        # determine the order to sort the articles
        if self.order and self.order.lower() == 'desc':
            order = '-created_date'
        else:
            order = 'created_date'

        user = context.get('user', None)

        # get the live articles in the appropriate order
        articles = Publication.objects.order_by(order).select_related()

        if self.count:
            # if we have a number of articles to retrieve, pull the first of them
            articles = articles[:int(self.count)]
        else:
            # get a range of articles
            articles = articles[(int(self.start) - 1):int(self.end)]

        # don't send back a list when we really don't need/want one
        if len(articles) == 1 and not self.start and int(self.count) == 1:
            articles = articles[0]

        # put the article(s) into the context
        context[self.varname] = articles
        return ''


def get_articles(parser, token):
    """
    Retrieves a list of Publication objects for use in a template.
    """
    args = token.split_contents()
    argc = len(args)

    try:
        assert argc in (4, 6) or (argc in (5, 7) and args[-1].lower() in ('desc', 'asc'))
    except AssertionError as aserr:
        raise template.TemplateSyntaxError('Invalid get_articles syntax.')

    # determine what parameters to use
    order = 'desc'
    count = start = end = varname = None
    if argc == 4:
        t, count, a, varname = args
    elif argc == 5:
        t, count, a, varname, order = args
    elif argc == 6:
        t, start, t, end, a, varname = args
    elif argc == 7:
        t, start, t, end, a, varname, order = args

    return GetPublicationsNode(count=count,
                               start=start,
                               end=end,
                               order=order,
                               varname=varname)


class GetPublicationArchivesNode(template.Node):
    """
    Retrieves a list of years and months in which articles have been posted.
    """

    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        cache_key = 'article_archive_list'
        dt_archives = cache.get(cache_key)
        if dt_archives is None:
            archives = {}
            user = context.get('user', None)

            # iterate over all live articles
            for article in Publication.objects.live(user=user).select_related():
                pub = article.created_date

                # see if we already have an article in this year
                if pub.year not in archives:
                    # if not, initialize a dict for the year
                    archives[pub.year] = {}

                # make sure we know that we have an article posted in this month/year
                archives[pub.year][pub.month] = True

            dt_archives = []

            # now sort the years, so they don't appear randomly on the page
            years = list(int(k) for k in archives.keys())
            years.sort()

            # more recent years will appear first in the resulting collection
            years.reverse()

            # iterate over all years
            for year in years:
                # sort the months of this year in which articles were posted
                m = list(int(k) for k in archives[year].keys())
                m.sort()

                # now create a list of datetime objects for each month/year
                months = [datetime(year, month, 1) for month in m]

                # append this list to our final collection
                dt_archives.append((year, tuple(months)))

            cache.set(cache_key, dt_archives)

        # put our collection into the context
        context[self.varname] = dt_archives
        return ''


def get_article_archives(parser, token):
    """
    Retrieves a list of years and months in which articles have been posted.
    """
    args = token.split_contents()
    argc = len(args)

    try:
        assert argc == 3 and args[1] == 'as'
    except AssertionError as aserr:
        raise template.TemplateSyntaxError('get_article_archives syntax: {% get_article_archives as varname %}')

    return GetPublicationArchivesNode(args[2])


register.tag(get_articles)
register.tag(get_article_archives)