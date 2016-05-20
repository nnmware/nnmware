# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib.admin.widgets import AdminTimeWidget
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _, get_language
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from nnmware.apps.booking.models import Hotel, Room, Booking, Discount, DISCOUNT_SPECIAL
from nnmware.apps.booking.models import RequestAddHotel, DISCOUNT_NOREFUND, DISCOUNT_CREDITCARD, \
    DISCOUNT_EARLY, DISCOUNT_LATER, DISCOUNT_PERIOD, DISCOUNT_PACKAGE, DISCOUNT_NORMAL, DISCOUNT_HOLIDAY, \
    DISCOUNT_LAST_MINUTE
from nnmware.apps.money.models import Bill
from nnmware.core.fields import ReCaptchaField
from nnmware.core.forms import UserFromRequestForm


class LocaleNamedForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(LocaleNamedForm, self).__init__(*args, **kwargs)
        if get_language() == 'ru':
            name = self.instance.name
            description = self.instance.description
        else:
            name = self.instance.name_en
            description = self.instance.description_en
        self.fields['name'] = forms.CharField(widget=forms.TextInput(attrs={'size': '25'}), initial=name)
        self.fields['description'] = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'wide',
                                                                                                  'rows': '5'}),
                                                     initial=description)

    def save(self, commit=True):
        if get_language() == 'ru':
            self.instance.name = self.cleaned_data['name']
            self.instance.description = self.cleaned_data['description']
        else:
            self.instance.name_en = self.cleaned_data['name']
            self.instance.description_en = self.cleaned_data['description']
        return super(LocaleNamedForm, self).save(commit=commit)


class CabinetInfoForm(UserFromRequestForm, LocaleNamedForm):
    time_on = forms.CharField(widget=AdminTimeWidget(), required=False)
    time_off = forms.CharField(widget=AdminTimeWidget(), required=False)

    class Meta:
        model = Hotel
        fields = ('option', 'time_on', 'time_off')

    def __init__(self, *args, **kwargs):
        super(CabinetInfoForm, self).__init__(*args, **kwargs)
        if get_language() == 'ru':
            schema_transit = self.instance.schema_transit
            paid_services = self.instance.paid_services
        else:
            schema_transit = self.instance.schema_transit_en
            paid_services = self.instance.paid_services_en
        self.fields['schema_transit'] = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'wide',
                                                                                                     'rows': '5'}),
                                                        initial=schema_transit)
        self.fields['paid_services'] = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'wide',
                                                                                                    'rows': '5'}),
                                                       initial=paid_services)
        if not self._user.is_superuser:
            self.fields['name'].widget.attrs['readonly'] = True

    def clean_name(self):
        if self._user.is_superuser:
            return self.cleaned_data['name']
        if get_language() == 'ru':
            return self.instance.name
        else:
            return self.instance.name_en

    def save(self, commit=True):
        if get_language() == 'ru':
            self.instance.schema_transit = self.cleaned_data['schema_transit']
            self.instance.paid_services = self.cleaned_data['paid_services']
        else:
            self.instance.schema_transit_en = self.cleaned_data['schema_transit']
            self.instance.paid_services_en = self.cleaned_data['paid_services']
        return super(CabinetInfoForm, self).save(commit=commit)


class CabinetRoomForm(LocaleNamedForm):

    class Meta:
        model = Room
        fields = ('option', 'typefood', 'surface_area')
        widgets = {
            'typefood': forms.RadioSelect(),
        }


class CabinetEditBillForm(forms.ModelForm):

    class Meta:
        model = Bill
        fields = ('date_billed', 'status', 'description_small', 'invoice_number', 'amount')


class RequestAddHotelForm(forms.ModelForm):
    city = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '35'}))
    address = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '35'}))
    name = forms.CharField(widget=forms.TextInput(attrs={'size': '35'}))
    email = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '35'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '35'}))
    fax = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '35'}))
    contact_email = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '35'}))
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '35'}))
    rooms_count = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': '35'}))

    class Meta:
        model = RequestAddHotel
        fields = ('city', 'address', 'name', 'email', 'phone', 'fax', 'contact_email',
                  'website', 'rooms_count', 'starcount')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(RequestAddHotelForm, self).__init__(*args, **kwargs)
        if not user.is_authenticated():
            self.fields['recaptcha'] = ReCaptchaField(error_messages={'required': _('This field is required'),
                                                                      'invalid': _('Answer is wrong')})


class UserCabinetInfoForm(UserFromRequestForm):

    class Meta:
        model = get_user_model()
        fields = (
            'first_name', 'last_name', 'subscribe')


class BookingAddForm(UserFromRequestForm):
    room_id = forms.CharField(max_length=30, required=False)
    settlement = forms.CharField(max_length=30, required=False)
    hid_method = forms.CharField(max_length=30, required=False)

    class Meta:
        model = Booking
        fields = (
            'from_date', 'to_date', 'first_name', 'middle_name', 'last_name', 'phone', 'email', 'guests', 'comment')

    def clean_hid_method(self):
        m = self.cleaned_data.get('hid_method')
        if m:
            raise forms.ValidationError(_("Spam."))
        return None

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise forms.ValidationError(_("Phone is required"))
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError(_("Email is required"))
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError(_("Email is wrong"))
        return email

    def clean(self):
        cleaned_data = super(BookingAddForm, self).clean()
        if not self._user.is_authenticated():
            email = cleaned_data.get('email')
            if get_user_model().objects.filter(email=email).exists():
                raise forms.ValidationError(_("Email already registered, please sign-in."))
        return cleaned_data


class AddDiscountForm(LocaleNamedForm):
    # TODO - Not used now(future)
    class Meta:
        model = Discount
        fields = ('name', 'choice', 'time_on', 'time_off', 'days', 'at_price_days', 'percentage', 'apply_norefund',
        'apply_creditcard', 'apply_package', 'apply_period')

    def __init__(self, *args, **kwargs):
        super(AddDiscountForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = False

    def clean_choice(self):
        choice = self.cleaned_data.get('choice')
        if choice == 0:
            raise forms.ValidationError(_("Discount not set"))
        return choice

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name.strip()) is 0:
            name = _("New discount from ") + now().strftime("%d.%m.%Y")
        return name

    def clean(self):
        cleaned_data = super(AddDiscountForm, self).clean()
        choice = cleaned_data.get("choice")
        need_del = []
        if choice == DISCOUNT_NOREFUND or choice == DISCOUNT_CREDITCARD:
            need_del = ['time_on', 'time_off', 'days', 'at_price_days', 'apply_norefund', 'apply_creditcard',
                        'apply_package', 'apply_period']
        elif choice == DISCOUNT_EARLY:
            need_del = ['time_on', 'time_off', 'at_price_days', 'apply_creditcard']
        elif choice == DISCOUNT_LATER:
            need_del = ['time_off', 'at_price_days']
        elif choice == DISCOUNT_PERIOD:
            need_del = ['time_on', 'time_off', 'at_price_days', 'apply_package', 'apply_period']
        elif choice == DISCOUNT_PACKAGE:
            need_del = ['time_on', 'time_off', 'apply_norefund', 'apply_creditcard']
        elif choice == DISCOUNT_HOLIDAY or choice == DISCOUNT_SPECIAL or choice == DISCOUNT_NORMAL:
            need_del = ['time_on', 'time_off', 'days', 'at_price_days', 'apply_package', 'apply_period']
        elif choice == DISCOUNT_LAST_MINUTE:
            need_del = ['days', 'at_price_days', 'apply_norefund', 'apply_creditcard', 'apply_package', 'apply_period']
        for i in need_del:
            del cleaned_data[i]
