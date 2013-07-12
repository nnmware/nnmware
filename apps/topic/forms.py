# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import ModelForm
from nnmware.apps.topic.models import TopicCategory, Topic
from django.utils.translation import ugettext_lazy as _


class TopicForm(ModelForm):
    category = forms.ModelChoiceField(queryset=TopicCategory.objects.filter(rootnode=False))

    class Meta:
        model = Topic
        fields = ('category', 'title', 'description')


class TopicAddForm(ModelForm):
    category = forms.ModelChoiceField(queryset=TopicCategory.objects.filter(rootnode=False))

    class Meta:
        model = Topic
        fields = ('category', 'name', 'description')


class AdminTopicForm(forms.ModelForm):
    class Meta:
        model = Topic

#        fields = ('is_sticky','is_closed','is_hidden','is_private')


class AddTopicForm(forms.ModelForm):

    class Meta:
        model = Topic
        fields = ('name', 'category', 'description')

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if not category:
            raise forms.ValidationError(_("Category is required"))
        return category
