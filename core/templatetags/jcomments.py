# -*- coding: utf-8 -*-

from django import template
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from nnmware.core.models import JComment

register = template.Library()

def get_contenttype_kwargs(content_object):
    """
    Gets the basic kwargs necessary for almost all of the following tags.
    """
    kwargs = {
        'content_type': ContentType.objects.get_for_model(content_object).id,
        'object_id': getattr(content_object, 'pk', getattr(content_object, 'id')),
        }
    return kwargs

@register.simple_tag
def get_file_attach_url(content_object):
    kwargs = get_contenttype_kwargs(content_object)
    return reverse('doc_ajax', kwargs=kwargs)

@register.simple_tag
def get_image_attach_url(content_object):
    kwargs = get_contenttype_kwargs(content_object)
    return reverse('pic_ajax', kwargs=kwargs)

@register.simple_tag
def get_comment_url(content_object, parent=None):
    """
    Given an object and an optional parent, this tag gets the URL to POST to for the
    creation of new ``ThreadedComment`` objects.
    """
    kwargs = get_contenttype_kwargs(content_object)
    if parent:
        if not isinstance(parent, JComment):
            raise template.TemplateSyntaxError, "get_comment_url requires its parent object to be of type JComment"
        kwargs.update({'parent_id': getattr(parent, 'pk', getattr(parent, 'id'))})
        return reverse('jcomment_parent_add', kwargs=kwargs)
    else:
        return reverse('jcomment_add', kwargs=kwargs)

@register.tag
def get_j_comment_tree(parser, token):
    """
    Gets a tree (list of objects ordered by preorder tree traversal, and with an
    additional ``depth`` integer attribute annotated onto each ``ThreadedComment``.
    """
    error_string = "%r tag must be of format {%% get_j_comment_tree for OBJECT [TREE_ROOT] as CONTEXT_VARIABLE %%}" % \
        token.contents.split()[0]

    try:
        split = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(error_string)
    if len(split) == 5:
        return CommentTreeNode(split[2], split[4], split[3])
    elif len(split) == 6:
        return CommentTreeNode(split[2], split[5], split[3])
    else:
        raise template.TemplateSyntaxError(error_string)


class CommentTreeNode(template.Node):
    def __init__(self, content_object, context_name, tree_root):
        self.content_object = template.Variable(content_object)
        self.tree_root = template.Variable(tree_root)
        self.tree_root_str = tree_root
        self.context_name = context_name

    def render(self, context):
        content_object = self.content_object.resolve(context)
        try:
            tree_root = self.tree_root.resolve(context)
        except template.VariableDoesNotExist:
            if self.tree_root_str == 'as':
                tree_root = None
            else:
                try:
                    tree_root = int(self.tree_root_str)
                except ValueError:
                    tree_root = self.tree_root_str
        context[self.context_name] = JComment.public.get_tree(content_object, root=tree_root)
        return ''

@register.tag
def get_comment_count(parser, token):
    """
    Gets a count of how many ThreadedComment objects are attached to the given
    object.
    """
    error_message = "%r tag must be of format {%% %r for OBJECT as CONTEXT_VARIABLE %%}" % (
        token.contents.split()[0], token.contents.split()[0])
    try:
        split = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, error_message
    if split[1] != 'for' or split[3] != 'as':
        raise template.TemplateSyntaxError, error_message
    return JCommentCountNode(split[2], split[4])


class JCommentCountNode(template.Node):
    def __init__(self, content_object, context_name):
        self.content_object = template.Variable(content_object)
        self.context_name = context_name

    def render(self, context):
        content_object = self.content_object.resolve(context)
        context[self.context_name] = JComment.public.all_for_object(content_object).count()
        return ''


@register.filter
def nerd_comment(value):
    return 59*value

@register.tag
def get_latest_comments(parser, token):
    """
    Gets the latest comments by date_submitted.
    """
    error_message = "%r tag must be of format {%% %r NUM_TO_GET as CONTEXT_VARIABLE %%}" % (
        token.contents.split()[0], token.contents.split()[0])
    try:
        split = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, error_message
    if len(split) != 4:
        raise template.TemplateSyntaxError, error_message
    if split[2] != 'as':
        raise template.TemplateSyntaxError, error_message
    return LatestCommentsNode(split[1], split[3])


class LatestCommentsNode(template.Node):
    def __init__(self, num, context_name):
        self.num = num
        self.context_name = context_name

    def render(self, context):
        comments = JComment.objects.order_by('-created_date')[:self.num]
        context[self.context_name] = comments
        return ''

@register.tag
def get_user_comments(parser, token):
    """
    Gets all comments submitted by a particular user.
    """
    error_message = "%r tag must be of format {%% %r for OBJECT as CONTEXT_VARIABLE %%}" % (
        token.contents.split()[0], token.contents.split()[0])
    try:
        split = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, error_message
    if len(split) != 5:
        raise template.TemplateSyntaxError, error_message
    return UserCommentsNode(split[2], split[4])


class UserCommentsNode(template.Node):
    def __init__(self, user, context_name):
        self.user = template.Variable(user)
        self.context_name = context_name

    def render(self, context):
        user = self.user.resolve(context)
        context[self.context_name] = user.jcomment_set.all()
        return ''

@register.tag
def get_user_comment_count(parser, token):
    """
    Gets the count of all comments submitted by a particular user.
    """
    error_message = "%r tag must be of format {%% %r for OBJECT as CONTEXT_VARIABLE %%}" % (
        token.contents.split()[0], token.contents.split()[0])
    try:
        split = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, error_message
    if len(split) != 5:
        raise template.TemplateSyntaxError, error_message
    return UserCommentCountNode(split[2], split[4])


class UserCommentCountNode(template.Node):
    def __init__(self, user, context_name):
        self.user = template.Variable(user)
        self.context_name = context_name

    def render(self, context):
        user = self.user.resolve(context)
        context[self.context_name] = user.jcomment_set.all().count()
        return ''
