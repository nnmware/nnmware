# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import ModelForm
from nnmware.core.forms import CategoryMixinForm
from nnmware.apps.topic.models import TopicCategory, Topic
from django.utils.translation import ugettext_lazy as _


class TopicForm(ModelForm):
    category = forms.ModelChoiceField(queryset=TopicCategory.objects.filter(rootnode=False))

    class Meta:
        model = Topic
        fields = ('category', 'name', 'description')


class TopicAddForm(ModelForm):
    category = forms.ModelChoiceField(queryset=TopicCategory.objects.filter(rootnode=False))

    class Meta:
        model = Topic
        fields = ('category', 'name', 'description')


class AdminTopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = '__all__'


class AddTopicForm(CategoryMixinForm):

    class Meta:
        model = Topic
        fields = ('name', 'category', 'description')
