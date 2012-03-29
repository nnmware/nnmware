from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from nnmware.core.models import NOTICE_UNKNOWN, ACTION_UNKNOWN
from nnmware.core.signals import action, notice



def follow(user, actor, send_action=True):
    """
    Creates a ``User`` -> ``Actor`` follow relationship such that the actor's
    activities appear in the user's stream.
    Also sends the ``<user> started following <actor>`` action signal.
    Returns the created ``Follow`` instance.
    If ``send_action`` is false, no "started following" signal will be created

    Syntax::

        follow(<user>, <actor>)

    Example::

        follow(request.user, group)

    """
    from nnmware.core.models import Follow

    follow, created = Follow.objects.get_or_create(user=user,
        object_id=actor.pk,
        content_type=ContentType.objects.get_for_model(actor))
    return created


def unfollow(user, actor, send_action=False):
    """
    Removes ``User`` -> ``Actor`` follow relationship.
    Optionally sends the ``<user> stopped following <actor>`` action signal.

    Syntax::

        unfollow(<user>, <actor>)

    Example::

        unfollow(request.user, other_user)

    """
    from nnmware.core.models import Follow

    Follow.objects.filter(user=user, object_id=actor.pk,
        content_type=ContentType.objects.get_for_model(actor)).delete()
    return True

def is_following(user, actor):
    """
    Checks if a ``User`` -> ``Actor`` relationship exists.
    Returns True if exists, False otherwise.

    Syntax::

        is_following(<user>, <actor>)

    Example::

        is_following(request.user, group)

    """
    from nnmware.core.models import Follow

    return bool(Follow.objects.filter(user=user, object_id=actor.pk,
        content_type=ContentType.objects.get_for_model(actor)).count())

def action_handler(verb, **kwargs):
    """
    Handler function to create Action instance upon action signal call.
    """
    from nnmware.core.models import Action

    kwargs.pop('signal', None)
    target = kwargs.pop('target', None)
    action = Action()
    action.user = kwargs.pop('sender')
    if target:
        action.content_type=ContentType.objects.get_for_model(target)
        action.object_id=target.pk
    action.verb=unicode(verb)
    action.action_type =kwargs.pop('action_type', ACTION_UNKNOWN)
    action.description=kwargs.pop('description', None)
    action.save()

def notice_handler(verb, **kwargs):
    """
    Handler function to create Notice instance upon action signal call.
    """
    from nnmware.core.models import Notice

    kwargs.pop('signal', None)
    target = kwargs.pop('target', None)
    notice = Notice()
    notice.user = kwargs.pop('user')
    notice.sender = kwargs.pop('sender')
    if target:
        notice.content_type=ContentType.objects.get_for_model(target)
        notice.object_id=target.pk
    notice.verb=unicode(verb)
    notice.notice_type =kwargs.pop('notice_type', NOTICE_UNKNOWN)
    notice.description=kwargs.pop('description', None)
    notice.save()

action.connect(action_handler, dispatch_uid='actstream.models')
notice.connect(notice_handler, dispatch_uid='notice_sender')
