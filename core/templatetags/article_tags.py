# nnmware(c)2012-2017

from __future__ import unicode_literals
from datetime import datetime
import math

from django import template
from django.core.cache import cache
from django.urls import resolve, reverse, Resolver404
from django.db.models import Count

# from nnmware.apps.publication.models import Publication
from nnmware.core.models import Tag

register = template.Library()


class GetCategoriesNode(template.Node):
    """
    Retrieves a list of live article tags and places it into the context
    """

    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        tags = Tag.objects.all()
        context[self.varname] = tags
        return ''


def get_article_tags(parser, token):
    """
    Retrieves a list of live article tags and places it into the context
    """
    args = token.split_contents()
    argc = len(args)

    try:
        assert argc == 3 and args[1] == 'as'
    except AssertionError as aserr:
        raise template.TemplateSyntaxError('get_article_tags syntax: {% get_article_tags as varname %}')
    return GetCategoriesNode(args[2])


class DivideObjectListByNode(template.Node):
    """
    Divides an object list by some number to determine now many objects will
    fit into, say, a column.
    """

    def __init__(self, object_list, divisor, varname):
        self.object_list = template.Variable(object_list)
        self.divisor = template.Variable(divisor)
        self.varname = varname

    def render(self, context):
        # get the actual object list from the context
        object_list = self.object_list.resolve(context)

        # get the divisor from the context
        divisor = int(self.divisor.resolve(context))

        # make sure we don't divide by 0 or some negative number!!!!!!
        assert divisor > 0

        context[self.varname] = int(math.ceil(len(object_list) / float(divisor)))
        return ''


def divide_object_list(parser, token):
    """
    Divides an object list by some number to determine now many objects will
    fit into, say, a column.
    """
    args = token.split_contents()
    argc = len(args)

    try:
        assert argc == 6 and args[2] == 'by' and args[4] == 'as'
    except AssertionError as aserr:
        raise template.TemplateSyntaxError(
            'divide_object_list syntax: {% divide_object_list object_list by divisor as varname %}')

    return DivideObjectListByNode(args[1], args[3], args[5])


class GetPageURLNode(template.Node):
    """
    Determines the URL of a pagination page link based on the page from which
    this tag is called.
    """

    def __init__(self, page_num, varname=None):
        self.page_num = template.Variable(page_num)
        self.varname = varname

    def render(self, context):
        url = None

        # get the page number we're linking to from the context
        page_num = self.page_num.resolve(context)

        try:
            # determine what view we are using based upon the path of this page
            view, args, kwargs = resolve(context['request'].path)
        except Resolver404 as rerr:
            raise ValueError('Invalid pagination page.')
        except KeyError as kerr:
            raise ValueError('Invalid pagination page.')
        else:
            # set the page parameter for this view
            kwargs['page'] = page_num
            # get the new URL from Django
            url = reverse(view, args=args, kwargs=kwargs)

        if self.varname:
            # if we have a varname, put the URL into the context and return nothing
            context[self.varname] = url
            return ''

        # otherwise, return the URL directly
        return url


def get_page_url(parser, token):
    """
    Determines the URL of a pagination page link based on the page from which
    this tag is called.
    """
    args = token.split_contents()
    argc = len(args)
    varname = None

    try:
        assert argc in (2, 4)
    except AssertionError as aerr:
        raise template.TemplateSyntaxError('get_page_url syntax: {% get_page_url page_num as varname %}')

    if argc == 4:
        varname = args[3]

    return GetPageURLNode(args[1], varname)


def tag_cloud():
    """Provides the tags with a "weight" attribute to build a tag cloud"""

    cache_key = 'tag_cloud_tags'
    tags = cache.get(cache_key)
    if tags is None:
        max_weight = 7
        tags = Tag.objects.annotate(count=Count('article'))

        if not len(tags):
            # go no further
            return {}

        min_count = max_count = tags[0].article_set.count()
        for tag in tags:
            if tag.count < min_count:
                min_count = tag.count
            if max_count < tag.count:
                max_count = tag.count

        # calculate count range, and avoid dbz
        _range = float(max_count - min_count)
        if _range == 0.0:
            _range = 1.0

        # calculate tag weights
        for tag in tags:
            tag.weight = int(max_weight * (tag.count - min_count) / _range)

        cache.set(cache_key, tags)

    return {'tags': tags}

# register dem tags!
register.tag(get_article_tags)
register.tag(divide_object_list)
register.tag(get_page_url)
register.inclusion_tag('articles/_tag_cloud.html')(tag_cloud)
