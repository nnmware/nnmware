# -*- coding: utf-8 -*-
from django import forms
from nnmware.apps.news.models import News
from django.utils.translation import ugettext_lazy as _


class AddNewsForm(forms.ModelForm):

    class Meta:
        model = News
        fields = ('name', 'category', 'description')

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if not category:
            raise forms.ValidationError(_("Category is required"))
        return category
