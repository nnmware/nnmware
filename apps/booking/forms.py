# -*- coding: utf-8 -*-

from django import forms
from nnmware.apps.booking.models import Hotel, HotelOption, Room

class CabinetInfoForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'size' : '25'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class' : 'wide','rows':'5'}))

    class Meta:
        model = Hotel
        fields = ('name', 'description', 'option')

class CabinetAddRoomForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'size' : '25'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class' : 'wide','rows':'5'}))

    class Meta:
        model = Room
        fields = ('name', 'description', 'option')

class CabinetEditRoomForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'size' : '25'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class' : 'wide','rows':'5'}))

    class Meta:
        model = Room
        fields = ('name', 'description', 'option')
