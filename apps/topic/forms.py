# -*- coding: utf-8 -*-
from django import forms
from nnmware.core.forms import CategoryMixinForm
from nnmware.apps.topic.models import TopicCategory, Topic
from django.utils.translation import ugettext_lazy as _


class TopicForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=TopicCategory.objects.filter(rootnode=False))

    class Meta:
        model = Topic
        fields = ('category', 'name', 'description')


class AdminTopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = '__all__'


class TopicAddForm(CategoryMixinForm):

    class Meta:
        model = Topic
        fields = ('name', 'category', 'description')
