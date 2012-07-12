import re
from django import template
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_str, force_unicode
from django.utils.safestring import mark_safe
from nnmware.core.models import JComment
from nnmware.core.forms import JCommentForm

# Regular expressions for getting rid of newlines and witespace
inbetween = re.compile('>[ \r\n]+<')
newlines = re.compile('\r|\n')

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


def get_file_attach_url(content_object):
    kwargs = get_contenttype_kwargs(content_object)
    return reverse('doc_ajax', kwargs=kwargs)


def get_image_attach_url(content_object):
    kwargs = get_contenttype_kwargs(content_object)
    return reverse('pic_ajax', kwargs=kwargs)


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


def get_comment_url_ajax(content_object, parent=None, ajax_type='json'):
    """
    Given an object and an optional parent, this tag gets the URL to POST to for the
    creation of new ``JComment`` objects.  It returns the latest created object
    in the AJAX form of the user's choosing (json or xml).
    """
    kwargs = get_contenttype_kwargs(content_object)
    kwargs.update({'ajax': ajax_type})
    if parent:
        if not isinstance(parent, JComment):
            raise template.TemplateSyntaxError, "get_comment_url_ajax requires its parent object to be of type ThreadedComment"
        kwargs.update({'parent_id': getattr(parent, 'pk', getattr(parent, 'id'))})
        return reverse('tc_comment_parent_ajax', kwargs=kwargs)
    else:
        return reverse('tc_comment_ajax', kwargs=kwargs)


def get_comment_url_json(content_object, parent=None):
    """
    Wraps ``get_comment_url_ajax`` with ``ajax_type='json'``
    """
    try:
        return get_comment_url_ajax(content_object, parent, ajax_type="json")
    except template.TemplateSyntaxError:
        raise template.TemplateSyntaxError, "get_comment_url_json requires its parent object to be of type ThreadedComment"


def get_comment_url_xml(content_object, parent=None):
    """
    Wraps ``get_comment_url_ajax`` with ``ajax_type='xml'``
    """
    try:
        return get_comment_url_ajax(content_object, parent, ajax_type="xml")
    except template.TemplateSyntaxError:
        raise template.TemplateSyntaxError, "get_comment_url_xml requires its parent object to be of type ThreadedComment"


def auto_transform_comment(comment):
    """
    Given a comment ``JComment`` , this tag
    looks up the markup type of the comment and formats the output accordingly.
    It can also output the formatted content to a context variable, if a context name is
    specified.
    """
    try:
        from django.utils.html import escape
        from nnmware.core.txtutil import smiles

        return smiles(comment.comment)
    except ImportError:
        # Not marking safe, in case tag fails and users input malicious code.
        return force_unicode(comment.comment)


def do_auto_transform_comment(parser, token):
    try:
        split = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag must be of format {%% %r COMMENT %%} or of format {%% %r COMMENT as CONTEXT_VARIABLE %%}" % (
            token.contents.split()[0], token.contents.split()[0], token.contents.split()[0])
    if len(split) == 2:
        return AutoTransformCommentNode(split[1])
    elif len(split) == 4:
        return AutoTransformCommentNode(split[1], context_name=split[3])
    else:
        raise template.TemplateSyntaxError, "Invalid number of arguments for tag %r" % split[0]


class AutoTransformCommentNode(template.Node):
    def __init__(self, comment, context_name=None):
        self.comment = template.Variable(comment)
        self.context_name = context_name

    def render(self, context):
        comment = self.comment.resolve(context)
        if self.context_name:
            context[self.context_name] = auto_transform_comment(comment)
            return ''
        else:
            return auto_transform_comment(comment)


def do_get_j_comment_tree(parser, token):
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


def do_get_comment_count(parser, token):
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


def oneline(value):
    """
    Takes some HTML and gets rid of newlines and spaces between tags, rendering
    the result all on one line.
    """
    try:
        return mark_safe(newlines.sub('', inbetween.sub('><', value)))
    except:
        return value

@register.filter
def nerd_comment(value):
    return 59*value

def do_get_j_comment_form(parser, token):
    """
    Gets a FreeThreadedCommentForm and inserts it into the context.
    """
    error_message = "%r tag must be of format {%% %r as CONTEXT_VARIABLE %%}" % (
        token.contents.split()[0], token.contents.split()[0])
    try:
        split = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, error_message
    if split[1] != 'as':
        raise template.TemplateSyntaxError, error_message
    if len(split) != 3:
        raise template.TemplateSyntaxError, error_message
    return JCommentFormNode(split[2])


class JCommentFormNode(template.Node):
    def __init__(self, context_name, free=False):
        self.context_name = context_name

    def render(self, context):
        form = JCommentForm()
        context[self.context_name] = form
        return ''


def do_get_latest_comments(parser, token):
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
        comments = JComment.objects.order_by('-publish_date')[:self.num]
        context[self.context_name] = comments
        return ''


def do_get_user_comments(parser, token):
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


def do_get_user_comment_count(parser, token):
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

register.simple_tag(get_comment_url)
register.simple_tag(get_file_attach_url)
register.simple_tag(get_image_attach_url)
register.simple_tag(get_comment_url_json)
register.simple_tag(get_comment_url_xml)

register.filter('oneline', oneline)

register.tag('auto_transform_comment', do_auto_transform_comment)
register.tag('get_j_comment_tree', do_get_j_comment_tree)
register.tag('get_comment_count', do_get_comment_count)
register.tag('get_j_comment_form', do_get_j_comment_form)
register.tag('get_latest_comments', do_get_latest_comments)
register.tag('get_user_comments', do_get_user_comments)
register.tag('get_user_comment_count', do_get_user_comment_count)
