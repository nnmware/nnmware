# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

from nnmware.apps.shop.models import Product, ProductParameter

class EditProductForm(forms.ModelForm):
    """
    Superuser edit product form
    """
    params = forms.ModelChoiceField(queryset=ProductParameter.objects.all(), required=False)
    class Meta:
        model = Product
        fields = ('name','category','slug','amount','quantity','avail','description',
            'shop_pn','vendor_pn','vendor','latest','teaser')

    def clean(self):
        return self.cleaned_data


