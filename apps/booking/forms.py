# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.booking.models import Hotel, HotelOption, Room
from nnmware.apps.booking.models import RequestAddHotel
from nnmware.core.fields import ReCaptchaField
from nnmware.core.middleware import get_request


class CabinetInfoForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'size' : '25'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class' : 'wide','rows':'5'}))

    class Meta:
        model = Hotel
        fields = ('name', 'description', 'option')

class CabinetAddRoomForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'size' : '25'}))
    description = forms.CharField(required=False,widget=forms.Textarea(attrs={'class' : 'wide','rows':'5'}))

    class Meta:
        model = Room
        fields = ('name', 'description', 'option','places')

class CabinetEditRoomForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'size' : '25'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class' : 'wide','rows':'5'}))

    class Meta:
        model = Room
        fields = ('name', 'description', 'option')

class RequestAddHotelForm(forms.ModelForm):
    city = forms.CharField(required=False, widget=forms.TextInput(attrs={'size' : '25'}))
    address = forms.CharField(required=False, widget=forms.TextInput(attrs={'size' : '32'}))
    name = forms.CharField(widget=forms.TextInput(attrs={'size' : '25'}))
    email = forms.CharField(required=False, widget=forms.TextInput(attrs={'size' : '25'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'size' : '25'}))
    fax = forms.CharField(required=False, widget=forms.TextInput(attrs={'size' : '25'}))
    contact_email = forms.CharField(required=False, widget=forms.TextInput(attrs={'size' : '25'}))
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={'size' : '25'}))
    rooms_count = forms.CharField(required=False, widget=forms.TextInput(attrs={'size' : '25'}))

    class Meta:
        model = RequestAddHotel
        fields = ('city', 'address', 'name','email','phone','fax','contact_email','website','rooms_count')

    def __init__(self, *args, **kwargs):
        super(RequestAddHotelForm, self).__init__(*args, **kwargs)
        if not get_request().user.is_authenticated():
            self.fields['recaptcha'] = ReCaptchaField(error_messages = { 'required': _('This field is required'),
                                                                       'invalid' : _('Answer is wrong') })

