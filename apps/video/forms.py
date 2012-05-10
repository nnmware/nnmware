# -*- coding: utf-8 -*-
from django import forms
from nnmware.core.forms import TagsMixinForm
from nnmware.apps.video.models import Video

class VideoAddForm(TagsMixinForm):


    class Meta:
        model = Video
        fields = ('project_url','project_name', 'video_url' ,'tags','description')
        widgets = dict(description=forms.Textarea)
