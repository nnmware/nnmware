# -*- encoding: utf-8 -*-

from django.template import Library
#from nnmware.apps.forum.models import Category

try:
    from xml.etree.ElementTree import Element, SubElement, tostring
except ImportError:
    from elementtree.ElementTree import Element, SubElement, tostring

register = Library()


def recurse_for_children(current_node, parent_node, show_empty=True):
    child_count = current_node.children.count()

    if show_empty or child_count > 0:
        temp_parent = SubElement(parent_node, 'li')
        attrs = {'href': current_node.get_absolute_url()}
        link = SubElement(temp_parent, 'a', attrs)
        link.text = current_node.name
        myval = SubElement(temp_parent, 'b')
        myval.text = " %s/%s" % (current_node.get_updated_count, current_node.get_valid_count)
        if child_count > 0:
            new_parent = SubElement(temp_parent, 'ul')
            children = current_node.children.all()
            for child in children:
                recurse_for_children(child, new_parent)


@register.simple_tag
def tree(app=None):
    exec("""from nnmware.apps.%s.models import Category""" % app)
    html = Element('root')
    for node in Category.objects.all():
        if not node.parent:
            recurse_for_children(node, html)
    return tostring(html, 'utf-8')

#@register.simple_tag
#def category_tree_series():
#    root = Element("root")
#    for cats in Category.objects.all().filter(slug='series'):
#        if not cats.parent:
#            recurse_for_children(cats, root)
#    return tostring(root, 'utf-8')
