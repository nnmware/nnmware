from django.utils.translation import ugettext_lazy as _

class SocialAuthBaseException(Exception):
    """Base class for pipeline exceptions."""
    pass


class StopPipeline(SocialAuthBaseException):
    """Stop pipeline process exception.
    Raise this exception to stop the rest of the pipeline process.
    """
    def __unicode__(self):
        return _('Stop pipeline')


class AuthException(SocialAuthBaseException):
    """Auth process exception."""
    def __init__(self, backend, *args, **kwargs):
        self.backend = backend
        super(AuthException, self).__init__(*args, **kwargs)


class AuthFailed(AuthException):
    """Auth process failed for some reason."""
    def __unicode__(self):
        if self.message == 'access_denied':
            return _('Authentication process was cancelled')
        else:
            return _('Authentication failed: %s') % super(AuthFailed, self).__unicode__()


class AuthCanceled(AuthException):
    """Auth process was canceled by user."""
    def __unicode__(self):
        return _('Authentication process canceled')


class AuthUnknownError(AuthException):
    """Unknown auth process error."""
    def __unicode__(self):
        msg = super(AuthUnknownError, self).__unicode__()
        return _('An unknown error happened while authenticating %s') % msg


class AuthTokenError(AuthException):
    """Auth token error."""
    def __unicode__(self):
        msg = super(AuthTokenError, self).__unicode__()
        return _('Token error: %s') % msg


class AuthMissingParameter(AuthException):
    """Missing parameter needed to start or complete the process."""
    def __init__(self, backend, parameter, *args, **kwargs):
        self.parameter = parameter
        super(AuthMissingParameter, self).__init__(backend, *args, **kwargs)

    def __unicode__(self):
        return _('Missing needed parameter %s') % self.parameter


class AuthStateMissing(AuthException):
    """State parameter is incorrect."""
    def __unicode__(self):
        return _('Session value state missing.')


class AuthStateForbidden(AuthException):
    """State parameter is incorrect."""
    def __unicode__(self):
        return _('Wrong state parameter given.')
