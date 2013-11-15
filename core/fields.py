import json
from django import forms
from django.conf import settings
from django.db import models
from django.db.models.fields import TextField
from django.db.models.fields.files import ImageField
from django.core.exceptions import ValidationError
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _
from nnmware.core.widgets import ReCaptchaWidget
from nnmware.core.captcha import submit


class ReCaptchaField(forms.CharField):
    default_error_messages = {'captcha_invalid': _('Invalid captcha')}

    def __init__(self, *args, **kwargs):
        self.widget = ReCaptchaWidget
        self.required = True
        super(ReCaptchaField, self).__init__(*args, **kwargs)

    def clean(self, values):
        super(ReCaptchaField, self).clean(values[1])
        recaptcha_challenge_value = smart_text(values[0])
        recaptcha_response_value = smart_text(values[1])
        check_captcha = submit(recaptcha_challenge_value, recaptcha_response_value, settings.RECAPTCHA_PRIVATE_KEY, {})
        if not check_captcha.is_valid:
            raise forms.ValidationError(self.error_messages['captcha_invalid'])
        return values[0]


class StdImageFormField(ImageField):
    def clean(self, data, initial=None):
        if data != '__deleted__':
            return super(StdImageFormField, self).clean(data, initial)
        else:
            return '__deleted__'


def std_text_field(verbose, max_length=255):
    return models.CharField(verbose_name=verbose, max_length=max_length, blank=True, default='')


def std_url_field(verbose, max_length=150):
    return models.URLField(verbose_name=verbose, max_length=max_length, blank=True, default='')


def std_email_field(verbose):
    return models.EmailField(verbose_name=verbose, blank=True, default='')
