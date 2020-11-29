# nnmware(c)2012-2020

from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _

from nnmware.apps.news.models import News


class AddNewsForm(forms.ModelForm):

    class Meta:
        model = News
        fields = ('name', 'category', 'description')

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if not category:
            raise forms.ValidationError(_("Category is required"))
        return category
