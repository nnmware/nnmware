# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.safestring import mark_safe
from django.conf import settings
from django import forms

from nnmware.core.captcha import displayhtml


class ReCaptchaWidget(forms.widgets.Widget):
    recaptcha_challenge_name = 'recaptcha_challenge_field'
    recaptcha_response_name = 'recaptcha_response_field'

    def render(self, name, value, attrs=None):
        return mark_safe('%s' % displayhtml(settings.RECAPTCHA_PUBLIC_KEY))

    def value_from_datadict(self, data, files, name):
        return [data.get(self.recaptcha_challenge_name, None), data.get(self.recaptcha_response_name, None)]
