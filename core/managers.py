# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Manager
from django.db.models import Q


class AbstractContentManager(Manager):

    def for_object(self, obj):
        object_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type__pk=object_type.id, object_id=obj.id)


def dfs(node, all_nodes, depth):
    """
     Performs a recursive depth-first search starting at ``node``.  This function
     also annotates an attribute, ``depth``, which is an integer that represents
     how deeply nested this node is away from the original object.
     """
    node.depth = depth
    to_return = [node, ]
    for subnode in all_nodes:
        if subnode.parent and subnode.parent.id == node.id:
            to_return.extend(dfs(subnode, all_nodes, depth + 1))
    return to_return


class NnmcommentManager(Manager):
    """
     A ``Manager`` which will be attached to each comment model.  It helps to facilitate
     the retrieval of comments in tree form and also has utility methods for
     creating and retrieving objects related to a specific content object.
     """

    def get_tree(self, content_object, root=None):
        """
          Runs a depth-first search on all comments related to the given content_object.
          This depth-first search adds a ``depth`` attribute to the comment which
          signifies how how deeply nested the comment is away from the original object.
          If root is specified, it will start the tree from that comment's ID.
          Ideally, one would use this ``depth`` attribute in the display of the comment to
          offset that comment by some specified length.
          The following is a (VERY) simple example of how the depth property might be used in a template:
          {% for comment in comment_tree %}
              <p style="margin-left: {{ comment.depth }}em">{{ comment.comment }}</p>
          {% endfor %}
          """
        content_type = ContentType.objects.get_for_model(content_object)
        children = list(self.get_query_set().filter(
            content_type=content_type,
            object_id=getattr(content_object, 'pk', getattr(content_object, 'id')),
        ).select_related().order_by('-created_date'))
        to_return = []
        if root:
            if isinstance(root, int):
                root_id = root
            else:
                root_id = root.id
            to_return = [c for c in children if c.id == root_id]
            if to_return:
                to_return[0].depth = 0
                for child in children:
                    if child.parent_id == root_id:
                        to_return.extend(dfs(child, children, 1))
        else:
            for child in children:
                if not child.parent:
                    to_return.extend(dfs(child, children, 0))
        return to_return

    def _generate_object_kwarg_dict(self, content_object, **kwargs):
        """
          Generates the most comment keyword arguments for a given ``content_object``.
          """
        kwargs['content_type'] = ContentType.objects.get_for_model(content_object)
        kwargs['object_id'] = getattr(content_object, 'pk', getattr(content_object, 'id'))
        return kwargs

    def create_for_object(self, content_object, **kwargs):
        """
          A simple wrapper around ``create`` for a given ``content_object``.
          """
        return self.create(**self._generate_object_kwarg_dict(content_object, **kwargs))

    def get_or_create_for_object(self, content_object, **kwargs):
        """
          A simple wrapper around ``get_or_create`` for a given ``content_object``.
          """
        return self.get_or_create(**self._generate_object_kwarg_dict(content_object, **kwargs))

    def get_for_object(self, content_object, **kwargs):
        """
          A simple wrapper around ``get`` for a given ``content_object``.
          """
        return self.get(**self._generate_object_kwarg_dict(content_object, **kwargs))

    def all_for_object(self, content_object, **kwargs):
        """
          Prepopulates a QuerySet with all comments related to the given ``content_object``.
          """
        return self.filter(**self._generate_object_kwarg_dict(content_object, **kwargs))


class PublicNnmcommentManager(NnmcommentManager):
    """
     A ``Manager`` which borrows all of the same methods from ``ThreadedCommentManager``,
     but which also restricts the queryset to only the published methods
     (in other words, ``is_public = True``).
     """

    def get_query_set(self):
        from nnmware.core.abstract import STATUS_PUBLISHED, STATUS_STICKY

        return super(NnmcommentManager, self).get_query_set().filter(Q(status=STATUS_PUBLISHED) | Q(status=STATUS_STICKY))


class FollowManager(AbstractContentManager):
    """
    Manager for Follow model.
    """

    def is_following(self, user, obj):
        """
        Check if a user is following an object.
        """
        if not user:
            return False
        queryset = self.for_object(obj)
        return queryset.filter(user=user).exists()

#    def users(self, user):
#        content_type = ContentType.objects.get_for_model(User).pk
#        return self.filter(content_type=content_type, user=user)

class FinancialManager(Manager):
    """
    Manager for Transaction model.
    """

    def for_object(self, instance):
        """
        Filter to a specific instance.
        """
        content_type = ContentType.objects.get_for_model(instance).pk
        return self.filter(target_ctype=content_type, target_oid=instance.pk)

class MessageManager(Manager):

    def inbox_for(self, user):
        """
        Returns all messages that were received by the given user and are not
        marked as deleted.
        """
        return self.filter(
            recipient=user,
            recipient_deleted_at__isnull=True,
        )

    def unread(self, user):
        """
        Returns all messages that were received by the given user and are not
        marked as read.
        """
        return self.filter(
            recipient=user,
            read_at__isnull=True,
        )

    def users(self, user):
        messages = self.filter(
            Q(recipient=user, recipient_deleted_at__isnull=True) |
            Q(sender=user, sender_deleted_at__isnull=True))
        senders = messages.values_list('sender',flat=True)
        recipients = messages.values_list('recipient',flat=True)
        return get_user_model().objects.exclude(pk=user.pk).filter(
            Q(pk__in=senders) | Q(pk__in=recipients)).order_by('username')

    def concrete_user(self, user, recipient):
        return self.filter(
            Q(recipient=user, recipient_deleted_at__isnull=True, sender=recipient) |
            Q(sender=user, sender_deleted_at__isnull=True, recipient=recipient)).order_by('sent_at')

    def messages(self, user):
        """
        Returns all messages that were received by the given user and are not
        marked as deleted.
        """
        return self.filter(
            Q(recipient=user, recipient_deleted_at__isnull=True) |
            Q(sender=user, sender_deleted_at__isnull=True)
        ).filter(parent_msg__isnull=True).order_by('-sent_at')


    def outbox_for(self, user):
        """
        Returns all messages that were sent by the given user and are not
        marked as deleted.
        """
        return self.filter(
            sender=user,
            sender_deleted_at__isnull=True,
        )

    def trash_for(self, user):
        """
        Returns all messages that were either received or sent by the given
        user and are marked as deleted.
        """
        return self.filter(
            recipient=user,
            recipient_deleted_at__isnull=False,
        ) | self.filter(
            sender=user,
            sender_deleted_at__isnull=False,
        )

class ProductManager(Manager):

    def active(self):
        return self.filter(avail=True,visible=True)

    def sale(self):
        return self.active().filter(discount=True)


    #    def active_date_sort(self):
    #        return self.filter(avail=True).order_by('-created_date')

    def latest(self):
        return self.active().filter(latest=True)

    def on_main(self):
        return self.filter(enabled=True,on_main=True).order_by('category')
