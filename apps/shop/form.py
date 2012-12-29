# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

from nnmware.apps.shop.models import Product, ProductParameter, Order, ProductColor, ProductMaterial, ProductCategory

class EditProductForm(forms.ModelForm):
    """
    Superuser edit product form
    """
    params = forms.ModelChoiceField(queryset=ProductParameter.objects.all(), required=False)
    class Meta:
        model = Product
        fields = ('name','category','slug','amount','quantity','avail','description',
            'shop_pn','vendor_pn','vendor','latest','teaser','discount','bestseller')

    def clean(self):
        return self.cleaned_data

class EditProductFurnitureForm(forms.ModelForm):
    colors = forms.ModelChoiceField(queryset=ProductColor.objects.all(), required=False)
    materials = forms.ModelChoiceField(queryset=ProductMaterial.objects.all(), required=False)
    category = forms.ModelChoiceField(queryset=ProductCategory.objects.exclude(rootnode=True))
    class Meta:
        model = Product
        fields = ('name','category','slug','amount','discount_percent','avail','description',
                  'vendor','width','height','depth','on_main')

class OrderStatusForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ('status',)

class OrderCommentForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ('comment',)

class OrderTrackingForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ('tracknumber','cargoservice')
