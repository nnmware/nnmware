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
    related_products = forms.ModelChoiceField(queryset=Product.objects.all(), required=False)
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

class AnonymousOrderAddForm(forms.ModelForm):
#    booking_terms = forms.CharField(widget=forms.Textarea(attrs={'class' : 'wide','rows':'5'}),required=False)
#    condition_cancellation = forms.CharField(widget=forms.Textarea(attrs={'class' : 'wide','rows':'5'}),required=False)
#    paid_services = forms.CharField(widget=forms.Textarea(attrs={'class' : 'wide','rows':'5'}),required=False)

    class Meta:
        model = Order
        fields = ('first_name', 'last_name','email', 'phone','address','buyer_comment')
