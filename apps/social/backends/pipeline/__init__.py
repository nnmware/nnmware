"""Django-Social-Auth Pipeline.

Pipelines must return a dictionary with values that will be passed as parameter
to next pipeline item. Pipelines must take **kwargs parameters to avoid
failure. At some point a pipeline entry must create a UserSocialAuth instance
and load it to the output if the user logged in correctly.
"""
import warnings

from django.conf import settings

from nnmware.apps.social.backends import get_backend, PIPELINE
from django.contrib.auth.models import User


USERNAME = 'username'
USERNAME_MAX_LENGTH = User._meta.get_field(USERNAME).max_length


def warn_setting(name, func_name):
    """Warn about deprecated settings."""
    if hasattr(settings, name):
        msg = '%s is deprecated, disable or override "%s" pipeline instead'
        warnings.warn(msg % (name, func_name))

from django.http import HttpResponseRedirect


def username(request, *args, **kwargs):
    if kwargs.get('user'):
        username = kwargs['user'].username
    else:
        username = request.session.get('saved_username')
    return { 'username': username }


def redirect_to_form(*args, **kwargs):
    if not kwargs['request'].session.get('saved_username') and kwargs.get('user') is None:
        return HttpResponseRedirect('/form/')
