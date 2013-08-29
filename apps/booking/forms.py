# -*- coding: utf-8 -*-

from django import forms
from django.contrib.admin.widgets import AdminTimeWidget
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _, get_language
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from nnmware.apps.booking.models import Hotel, Room, Booking, Discount
from nnmware.apps.booking.models import RequestAddHotel, PaymentMethod
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

    class Meta:
        model = Hotel
        fields = ('option',)

    def __init__(self, *args, **kwargs):
        super(CabinetInfoForm, self).__init__(*args, **kwargs)
        if get_language() == 'ru':
            schema_transit = self.instance.schema_transit
        else:
            schema_transit = self.instance.schema_transit_en
        self.fields['schema_transit'] = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'wide',
                                                                                                     'rows': '5'}),
                                                        initial=schema_transit)
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
        else:
            self.instance.schema_transit_en = self.cleaned_data['schema_transit']
        return super(CabinetInfoForm, self).save(commit=commit)


class CabinetTermsForm(forms.ModelForm):
    time_on = forms.CharField(widget=AdminTimeWidget(), required=False)
    time_off = forms.CharField(widget=AdminTimeWidget(), required=False)

    class Meta:
        model = Hotel
        fields = ('payment_method', 'time_on', 'time_off')

    def __init__(self, *args, **kwargs):
        super(CabinetTermsForm, self).__init__(*args, **kwargs)
        if get_language() == 'ru':
            booking_terms = self.instance.booking_terms
            condition_cancellation = self.instance.condition_cancellation
            paid_services = self.instance.paid_services
        else:
            booking_terms = self.instance.booking_terms_en
            condition_cancellation = self.instance.condition_cancellation_en
            paid_services = self.instance.paid_services_en
        self.fields['booking_terms'] = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'wide',
                                                                                                    'rows': '5'}),
                                                       initial=booking_terms)
        self.fields['condition_cancellation'] = forms.CharField(required=False, widget=forms.Textarea(attrs={
            'class': 'wide', 'rows': '5'}), initial=condition_cancellation)
        self.fields['paid_services'] = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'wide',
                                                                                                    'rows': '5'}),
                                                       initial=paid_services)

    def save(self, commit=True):
        if get_language() == 'ru':
            self.instance.booking_terms = self.cleaned_data['booking_terms']
            self.instance.condition_cancellation = self.cleaned_data['condition_cancellation']
            self.instance.paid_services = self.cleaned_data['paid_services']
        else:
            self.instance.booking_terms_en = self.cleaned_data['booking_terms']
            self.instance.condition_cancellation_en = self.cleaned_data['condition_cancellation']
            self.instance.paid_services_en = self.cleaned_data['paid_services']
        return super(CabinetTermsForm, self).save(commit=commit)


class CabinetRoomForm(LocaleNamedForm):

    class Meta:
        model = Room
        fields = ('option', 'typefood')
        widgets = {
            'typefood': forms.RadioSelect(),
        }


class CabinetEditBillForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'wide', 'rows': '5', 'cols': '40'}))

    class Meta:
        model = Bill
        fields = ('date_billed', 'status', 'description', 'amount', 'currency')


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
    password = forms.CharField(label=_('New Password'), max_length=30, required=False)

    class Meta:
        model = get_user_model()
        fields = (
            'first_name', 'last_name', 'subscribe')

    def clean_password(self):
        password = self.cleaned_data["password"]
        if len(password.strip(' ')) > 0:
            if not self._user.check_password(password):
                self._user.set_password(password)
                self._user.save()
        return password

    # def clean_email(self):
    #     email = self.cleaned_data["email"]
    #     if get_user_model().objects.exclude(username=self.current_user.username).filter(email=email).exists():
    #         raise forms.ValidationError(_("Email already exist."))
    #     return email


class BookingAddForm(UserFromRequestForm):
    room_id = forms.CharField(max_length=30, required=False)
    settlement = forms.CharField(max_length=30, required=False)
    payment_method = forms.CharField(max_length=30, required=False)
    hid_method = forms.CharField(max_length=30, required=False)

    class Meta:
        model = Booking
        fields = (
            'from_date', 'to_date', 'first_name', 'middle_name', 'last_name', 'phone', 'email',
            'payment_method', 'guests')

    def clean_payment_method(self):
        p_m = self.cleaned_data.get('payment_method')
        if p_m:
            payment_method = PaymentMethod.objects.get(pk=int(p_m))
            return payment_method
        raise forms.ValidationError(_("No valid payment method."))

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


class BookingStatusForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'wide', 'rows': '5', 'cols': '40'}),
                                  required=False)

    class Meta:
        model = Booking
        fields = ('status', 'description')


class AddDiscountForm(LocaleNamedForm):

    class Meta:
        model = Discount
        fields = ('name', 'choice')
