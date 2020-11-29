# nnmware(c)2012-2020

from __future__ import unicode_literals

from django import forms

from nnmware.core.forms import CategoryMixinForm, DescriptionMixinForm, NameMixinForm
from nnmware.apps.topic.models import TopicCategory, Topic


class TopicForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=TopicCategory.objects.filter(rootnode=False))

    class Meta:
        model = Topic
        fields = ('category', 'name', 'description')


class AdminTopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = '__all__'


class TopicAddForm(NameMixinForm, CategoryMixinForm, DescriptionMixinForm):

    class Meta:
        model = Topic
        fields = ('name', 'category', 'description')
