"""Django ORM models for Social Auth"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.social.base import UserSocialAuthMixin, AssociationMixin, NonceMixin
from nnmware.core.fields import JSONField

class UserSocialAuth(models.Model, UserSocialAuthMixin):
    """Social Auth association model"""
    User = get_user_model()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='social_auth')
    provider = models.CharField(max_length=32)
    uid = models.CharField(max_length=255)
    extra_data = JSONField(default='{}')

    class Meta:
        """Meta data"""
        unique_together = ('provider', 'uid')
        app_label = 'social'
        verbose_name = _("User Social Auth")
        verbose_name_plural = _("User Social Auth")


    @classmethod
    def create_user(cls, *args, **kwargs):
        return cls.User.objects.create_user(*args, **kwargs)

    @classmethod
    def get_social_auth(cls, provider, uid):
        try:
            return cls.objects.select_related('user').get(provider=provider,
                uid=uid)
        except UserSocialAuth.DoesNotExist:
            return None

    @classmethod
    def username_max_length(cls):
        return cls.User._meta.get_field('username').max_length


class Nonce(models.Model, NonceMixin):
    """One use numbers"""
    server_url = models.CharField(max_length=255)
    timestamp = models.IntegerField()
    salt = models.CharField(max_length=40)

    class Meta:
        app_label = 'social'


class Association(models.Model, AssociationMixin):
    """OpenId account association"""
    server_url = models.CharField(max_length=255)
    handle = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)  # Stored base64 encoded
    issued = models.IntegerField()
    lifetime = models.IntegerField()
    assoc_type = models.CharField(max_length=64)

    class Meta:
        app_label = 'social'
