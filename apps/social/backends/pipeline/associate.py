from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from nnmware.apps.social.models import UserSocialAuth
from nnmware.apps.social.backends.exceptions import AuthException


def associate_by_email(details, user=None, *args, **kwargs):
    """Return user entry with same email address as one returned on details."""
    if user:
        return None

    email = details.get('email')

    if email:
        # try to associate accounts registered with the same email address,
        # only if it's a single object. AuthException is raised if multiple
        # objects are returned
        try:
            return {'user': UserSocialAuth.get_user_by_email(email=email)}
        except MultipleObjectsReturned:
            raise AuthException(kwargs['backend'], 'Not unique email address.')
        except ObjectDoesNotExist:
            pass
