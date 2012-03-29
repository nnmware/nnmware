# -*- coding: utf-8 -*-

from django import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from nnmware.apps.captcha import generate, test_solution


class ImageWidget(forms.Widget):
    def render(self, name, value, attrs=None):
        return forms.HiddenInput().render(name,
        value) + \
        u'<img class="captcha-image" src="%s" alt="captcha image" />' % value


class CaptchaWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        if not attrs:
            attrs = {}
        widgets = (forms.HiddenInput(),
                    ImageWidget(),
                    forms.TextInput(attrs={'class': 'captcha-input'}),
            )
        #self._test_id = None
        super(CaptchaWidget, self).__init__(widgets, attrs)

    def format_output(self, widgets):
        return u'%s%s%s' % (widgets[0], widgets[1], widgets[2])

    def decompress(self, value):
        # id - 0
        # image - 1
        # word - 2
        #self._test_id = test.id
        captcha_id = generate()
        return (
            captcha_id,
            reverse('captcha_image', args=[captcha_id]),
            '')


class CaptchaField(forms.Field):
    widget = CaptchaWidget

    def __init__(self, *args, **kwargs):
        super(CaptchaField, self).__init__(*args, **kwargs)
        self.label = _(u'Captcha')
        self.help_text = _(u'Please, enter symbols, which '
                           u'you see on the image')

    def clean(self, values):
        """Test the solution
        Input:
        0 - captcha_id, 1 - image URL, 2 - solution
        """

        if not test_solution(values[0], values[2]):
            raise forms.ValidationError(_(u'Wrong answer'))
        return values
