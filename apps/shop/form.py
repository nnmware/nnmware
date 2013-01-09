# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

from nnmware.apps.shop.models import Product, ProductParameter, Order, ProductColor, ProductMaterial, ProductCategory
from nnmware.apps.shop.models import DeliveryMethod

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

class AnonymousUserOrderAddForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ('first_name', 'last_name','email', 'phone','address','buyer_comment', 'delivery')

    def __init__(self, *args, **kwargs):
        super(AnonymousUserOrderAddForm, self).__init__(*args, **kwargs)
        self.fields['delivery'].queryset = DeliveryMethod.objects.all()

    def clean_first_name(self):
        first_name =  self.cleaned_data['first_name']
        if first_name:
            return first_name
        raise forms.ValidationError(_("Required field"))

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if last_name:
            return last_name
        raise forms.ValidationError(_("Required field"))

    def clean_email(self):
        email = self.cleaned_data['email']
        if email:
            return email
        raise forms.ValidationError(_("Required field"))

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if phone:
            return phone
        raise forms.ValidationError(_("Required field"))

    def clean_address(self):
        address = self.cleaned_data['address']
        if address:
            return address
        raise forms.ValidationError(_("Required field"))

    def clean_delivery(self):
        delivery = self.cleaned_data['delivery']
        if delivery:
            return delivery
        raise forms.ValidationError(_("Required field"))

class RegisterUserOrderAddForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ('buyer_comment', 'delivery')

    def __init__(self, *args, **kwargs):
        super(RegisterUserOrderAddForm, self).__init__(*args, **kwargs)
        self.fields['delivery'].queryset = DeliveryMethod.objects.all()

    def clean_delivery(self):
        delivery = self.cleaned_data['delivery']
        if delivery:
            return delivery
        raise forms.ValidationError(_("Required field"))
