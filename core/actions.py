# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType

from nnmware.core.constants import NOTICE_UNKNOWN, ACTION_UNKNOWN
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

    follow_, created = Follow.objects.get_or_create(user=user, object_id=actor.pk,
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
    action_ = Action()
    action_.user = kwargs.pop('sender')
    if target:
        action_.content_type = ContentType.objects.get_for_model(target)
        action_.object_id = target.pk
    action_.verb = unicode(verb)
    action_.action_type = kwargs.pop('action_type', ACTION_UNKNOWN)
    action_.description = kwargs.pop('description', None)
    request = kwargs.pop('request', None)
    if request:
        action_.ip = request.META['REMOTE_ADDR']
        action_.user_agent = request.META['HTTP_USER_AGENT']
    action_.save()


def notice_handler(verb, **kwargs):
    """
    Handler function to create Notice instance upon action signal call.
    """
    from nnmware.core.models import Notice

    kwargs.pop('signal', None)
    target = kwargs.pop('target', None)
    notice_ = Notice()
    notice_.user = kwargs.pop('user')
    notice_.sender = kwargs.pop('sender')
    if target:
        notice_.content_type = ContentType.objects.get_for_model(target)
        notice_.object_id = target.pk
    notice_.verb = unicode(verb)
    notice_.notice_type = kwargs.pop('notice_type', NOTICE_UNKNOWN)
    notice_.description = kwargs.pop('description', None)
    request = kwargs.pop('request', None)
    if request:
        notice_.ip = request.META['REMOTE_ADDR']
        notice_.user_agent = request.META['HTTP_USER_AGENT']
    notice_.save()

action.connect(action_handler, dispatch_uid='nnmware_action')
notice.connect(notice_handler, dispatch_uid='notice_sender')
