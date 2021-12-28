# nnmware(c)2012-2020

from __future__ import unicode_literals
from decimal import Decimal

from django.forms import CharField, ValidationError
from django.conf import settings
from django.db import models
from django.utils.encoding import smart_str
from django.utils.translation import gettext as _

from nnmware.core.widgets import ReCaptchaWidget
from nnmware.core.captcha import submit


class ReCaptchaField(CharField):
    default_error_messages = {'captcha_invalid': _('Invalid captcha')}

    def __init__(self, *args, **kwargs):
        self.widget = ReCaptchaWidget
        self.required = True
        super(ReCaptchaField, self).__init__(*args, **kwargs)

    def clean(self, values):
        super(ReCaptchaField, self).clean(values[1])
        recaptcha_challenge_value = smart_str(values[0])
        recaptcha_response_value = smart_str(values[1])
        check_captcha = submit(recaptcha_challenge_value, recaptcha_response_value, settings.RECAPTCHA_PRIVATE_KEY, {})
        if not check_captcha.is_valid:
            raise ValidationError(self.error_messages['captcha_invalid'])
        return values[0]


def std_text_field(verbose, max_length=255):
    return models.CharField(verbose_name=verbose, max_length=max_length, blank=True, default='')


def std_url_field(verbose, max_length=150):
    return models.URLField(verbose_name=verbose, max_length=max_length, blank=True, default='')


def std_email_field(verbose):
    return models.EmailField(verbose_name=verbose, blank=True, default='')


def std_btc_field(verbose):
    return models.DecimalField(verbose_name=verbose, max_digits=20, default=Decimal(0), decimal_places=8)
