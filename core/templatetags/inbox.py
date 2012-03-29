from django.template import Library, Node
from nnmware.core.models import Message

register = Library()


class InboxUnread(Node):
    def render(self, context):
        try:
            user = context['user']
            count = user.received_messages.filter(read_at__isnull=True, recipient_deleted_at__isnull=True).count()
        except (KeyError, AttributeError):
            count = ''
        return "%s" % count


class InboxCount(Node):
    def render(self, context):
        try:
            user = context['user']
            count = Message.objects.inbox_for(user).count()
        except (KeyError, AttributeError):
            count = ''
        return "%s" % count


class OutboxCount(Node):
    def render(self, context):
        try:
            user = context['user']
            count = Message.objects.outbox_for(user).count()
        except (KeyError, AttributeError):
            count = ''
        return "%s" % count


class TrashCount(Node):
    def render(self, context):
        try:
            user = context['user']
            count = Message.objects.trash_for(user).count()
        except (KeyError, AttributeError):
            count = ''
        return "%s" % count


@register.tag
def inbox_count(parser, token):
    """
    A templatetag to show the count mess for a logged in user.
    Prints the number of unread messages in the user's inbox.
    Usage::
        {% load inbox %}
        {% inbox_count %}
    """
    return InboxCount()


@register.tag
def inbox_unread(parser, token):
    return InboxUnread()


@register.tag
def outbox_count(parser, token):
    return OutboxCount()


@register.tag
def trash_count(parser, token):
    return TrashCount()
