# -*- encoding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import get_user_model
from django.template import Library
from django.template.base import Template
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from nnmware.core.abstract import Tree
from nnmware.core.data import *

from xml.etree.ElementTree import Element, SubElement, tostring

register = Library()

@register.simple_tag
def menu(app=None):
    if app == 'topic':
        from nnmware.apps.topic.models import Category as Tree
    elif app == 'board':
        from nnmware.apps.board.models import Category as Tree
    elif app == 'shop':
        from nnmware.apps.shop.models import ProductCategory as Tree
    elif app == 'article':
        from nnmware.apps.article.models import Category as Tree
    elif app == 'dashboard':
        from nnmware.apps.dashboard.models import Category as Tree
    else:
        pass

    if 1>0: #try:
        html = Element("ul")
        for node in Tree.objects.all():
            if not node.parent:
                recurse_for_children(node, html)
        return tostring(html, 'utf-8')
#    except:
#        return 'error'


@register.simple_tag
def category_tree_series():
    root = Element("ul")
    for cats in Tree.objects.all().filter(slug='series'):
        if not cats.parent:
            recurse_for_children(cats, root)
    return tostring(root, 'utf-8')


@register.simple_tag
def menu_user(app=None):
    if app == 'users':
        Alldata = get_user_model()
    query = Alldata.objects.all().order_by('-date_joined')
    objects_years_dict = create_userdate_list(query)
    html = Element("ul")
    keyList = objects_years_dict.keys()
    for key in keyList:
        recurse_for_date(app, key, objects_years_dict[key], html)
    return tostring(html, 'utf-8')


@register.simple_tag
def menu_date(app=None):
    if app == 'article':
        from nnmware.apps.article.models import Article as Alldata
    elif app == 'topic':
        from nnmware.apps.topic.models import Topic as Alldata
    elif app == 'pic':
        from nnmware.core.models import Pic as Alldata
    elif app == 'doc':
        from nnmware.core.models import Doc as Alldata
    query = Alldata.objects.all().order_by('-created_date')
    objects_years_dict = create_archive_list(query)
    html = Element("ul")
    keyList = objects_years_dict.keys()
    for key in keyList:
        recurse_for_date(app, key, objects_years_dict[key], html)
    return tostring(html, 'utf-8')
