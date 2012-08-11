# -*- coding: utf-8 -*-
import os

from django import forms
from django.conf import settings
from django.forms.widgets import RadioSelect
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _

from nnmware.core.models import JComment, Pic, Tag, Doc
from nnmware.core.utils import tags_normalize
from nnmware.core.widgets import AutocompleteWidget

DEFAULT_MAX_JCOMMENT_LENGTH = getattr(settings, 'DEFAULT_MAX_JCOMMENT_LENGTH', 1000)
DEFAULT_MAX_JCOMMENT_DEPTH = getattr(settings, 'DEFAULT_MAX_JCOMMENT_DEPTH', 8)


class TagsMixinForm(forms.ModelForm):
    tags = forms.CharField(label=_(u"Tags"))  #, widget=AutocompleteWidget(choices_url='autocomplete_tags'))

    def clean_tags(self):
        """
        Convert tags in string and check max number of tags for object
        If not found - make new tag
        """
        tags = set(tags_normalize(self.cleaned_data.get("tags")))
        if len(tags) > settings.TAGS_MAX:
            raise forms.ValidationError(_("Max number or tags - %s.") % settings.TAGS_MAX)
        alltags = Tag.objects.filter(name__in=tags).values_list('name', flat=True)
        for tag in tags:
            if tag not in alltags:
                Tag(name=tag).save()
        return tags

class JCommentForm(forms.ModelForm):
    """
    Form which can be used to validate data for a new ThreadedComment.
    It consists of just two fields: ``comment``, and ``markup``.
    The ``comment`` field is the only one which is required.
    """

    comment = forms.CharField(label=_('comment', ), max_length=DEFAULT_MAX_JCOMMENT_LENGTH, widget=forms.Textarea)

    class Meta:
        model = JComment
        fields = ('comment',)


class JCommentStatusForm(forms.ModelForm):
    class Meta:
        model = JComment
        fields = ('status', 'created_date')


class JCommentEditorForm(forms.ModelForm):
    comment = forms.CharField(label=_('comment', ),
        max_length=DEFAULT_MAX_JCOMMENT_LENGTH, widget=forms.Textarea)

    class Meta:
        model = JComment
        fields = ('comment',)


class JCommentEditorStatusForm(forms.ModelForm):
    class Meta:
        model = JComment
        fields = ('status', 'created_date')


class JCommentAdminForm(forms.ModelForm):
    comment = forms.CharField(label=_('comment', ),
        max_length=DEFAULT_MAX_JCOMMENT_LENGTH, widget=forms.Textarea)

    class Meta:
        model = JComment
        fields = ('comment',)


class JCommentAdminStatusForm(forms.ModelForm):
    class Meta:
        model = JComment
        fields = ('status', 'created_date')


class DocForm(forms.ModelForm):
    class Meta(object):
        model = Doc
        fields = ('file', 'description', 'created_date', 'locked', 'filetype')


class DocDeleteForm(forms.ModelForm):
    class Meta(object):
        model = Doc
        fields = ()

EDITOR_ACTION = (('rotate90', _('Rotate 90')), ('rotate270', _('Rotate 270')),
                 ('resize', _('Resize')))


class PicEditorForm(forms.ModelForm):
    """
    Crop dimensions form
    """
    top = forms.IntegerField()
    left = forms.IntegerField()
    right = forms.IntegerField()
    bottom = forms.IntegerField()
    editor_action = \
        forms.ChoiceField(widget=RadioSelect, choices=EDITOR_ACTION)


class UploadPicForm(forms.Form):

    pic = forms.ImageField()

    def __init__(self, *args, **kwargs):
        size = kwargs.pop('size', settings.PIC_DEFAULT_SIZE)
#        self.target = kwargs.pop('target')
        super(UploadPicForm, self).__init__(*args, **kwargs)

    def clean_pic(self):
        data = self.cleaned_data['pic']
        if settings.PIC_ALLOWED_FILE_EXTS:
            (root, ext) = os.path.splitext(data.name.lower())
            if ext not in settings.PIC_ALLOWED_FILE_EXTS:
                raise forms.ValidationError(
                    _(u"%(ext)s is an invalid file extension. "
                      u"Authorized extensions are : %(valid_exts_list)s") %
                    {'ext': ext,
                     'valid_exts_list': ", ".join(settings.PIC_ALLOWED_FILE_EXTS)})
        if data.size > settings.PIC_MAX_SIZE:
            raise forms.ValidationError(
                _(u"Your file is too big (%(size)s), "
                  u"the maximum allowed size is %(max_valid_size)s") %
                {'size': filesizeformat(data.size),
                 'max_valid_size': filesizeformat(settings.AVATAR_MAX_SIZE)})
        count = Pic.objects.metalinks_for_object(self.target).count()
        if count >= settings.PIC_MAX_PER_OBJECT > 1:
            raise forms.ValidationError(
                _(u"You already have %(nb_pic)d image, and the "
                  u"maximum allowed is %(nb_max_pic)d.") %
                {'nb_pic': count, 'nb_max_pic': settings.PIC_MAX_PER_OBJECT})
        return
