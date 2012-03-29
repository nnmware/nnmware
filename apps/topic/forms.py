from django import forms
from django.forms.models import ModelForm

from nnmware.apps.topic.models import Category, Topic
from django.utils.translation import ugettext_lazy as _


class TopicForm(ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.filter(rootnode=False))

    class Meta:
        model = Topic
        fields = ('category', 'title', 'description')


class TopicAddForm(ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.filter(rootnode=False))

    class Meta:
        model = Topic
        fields = ('category', 'title', 'description')


class AdminTopicForm(forms.ModelForm):
    class Meta:
        model = Topic

#        fields = ('is_sticky','is_closed','is_hidden','is_private')
