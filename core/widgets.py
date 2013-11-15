# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.conf import settings
from django import forms
from django.forms import Textarea, FileInput

from nnmware.core.imgutil import make_admin_thumbnail
from nnmware.core.captcha import displayhtml


class ReCaptchaWidget(forms.widgets.Widget):
    recaptcha_challenge_name = 'recaptcha_challenge_field'
    recaptcha_response_name = 'recaptcha_response_field'

    def render(self, name, value, attrs=None):
        return mark_safe('%s' % displayhtml(settings.RECAPTCHA_PUBLIC_KEY))

    def value_from_datadict(self, data, files, name):
        return [data.get(self.recaptcha_challenge_name, None), data.get(self.recaptcha_response_name, None)]


class CommentSmileWidget(Textarea):
    class Media:
        js = ('js/smile.js',)


class AdminImageWithThumbnailWidget(FileInput):
    """
    A FileField Widget that shows its current image as a thumbnail if it has one.
    """

    def __init__(self, attrs=None):
        if not attrs:
            attrs = {}
        super(AdminImageWithThumbnailWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = []
        if value and hasattr(value, "url"):
            thumb = make_admin_thumbnail(value.url)
            if not thumb:
                thumb = value.url
            output.append('<a href="%s"><img src="%s" /><br/>%s</a><br/> %s' %
                          (value.url, thumb, value.url, _('Change:')))
        output.append(super(AdminImageWithThumbnailWidget, self).render(name, value, attrs))
        output.append('<input type="checkbox" name="%s_delete"/> %s' % (name, _('Delete')))

        return mark_safe(''.join(output))

    def value_from_datadict(self, data, files, name):
        if not data.get('%s_delete' % name):
            return super(AdminImageWithThumbnailWidget, self).value_from_datadict(data, files, name)
        else:
            return '__deleted__'


class ImageWithThumbnailWidget(FileInput):
    """
    A FileField Widget that shows its current image as a thumbnail if it has one.
    """

    def __init__(self, attrs=None):
        if not attrs:
            attrs = {}
        super(ImageWithThumbnailWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = []
        if value and hasattr(value, "url"):
            thumb = make_admin_thumbnail(value.url)
            if not thumb:
                thumb = value.url
            output.append('<img src="%s" /><br/><input type="checkbox" name="%s_delete"/>%s<br/> %s' %
                          (thumb, name, _('Delete'), _('Change:')))
        output.append(super(ImageWithThumbnailWidget, self).render(name, value, attrs))
        return mark_safe(''.join(output))

    def value_from_datadict(self, data, files, name):
        if not data.get('%s_delete' % name):
            return super(ImageWithThumbnailWidget, self).value_from_datadict(data, files, name)
        else:
            return '__deleted__'
