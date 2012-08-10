# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

from nnmware.apps.shop.models import Product

class EditProductForm(forms.ModelForm):
    """
    Superuser edit product form
    """
    class Meta:
        model = Product
        fields = ('name','category','slug','amount','quantity')

    def clean(self):
        return self.cleaned_data


