# -*- coding: utf-8 -*-
from django import forms
from nnmware.apps.shop.models import Product

class EditProductForm(forms.ModelForm):
    """
    Superuser edit product form
    """
    class Meta:
        model = Product
        fields = ('name','category','slug','amount','quantity')

    def clean(self):
        if not (self.cleaned_data.get('avatar')):
            raise forms.ValidationError(_('You must enter one of the options'))
        return self.cleaned_data


