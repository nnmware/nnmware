# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from nnmware.core.fields import ReCaptchaField

from nnmware.apps.userprofile.models import Profile, EmailValidation


class RegistrationForm(UserCreationForm):
    """
    Form for registering a new user userprofile.
    """

    class Meta:
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        if settings.CAPTCHA_ENABLED:
            self.fields['recaptcha'] = ReCaptchaField(error_messages = { 'required': _('This field is required'),
                                                                       'invalid' : _('Answer is wrong') })
        super(RegistrationForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        """
        Verify that the email exists
        """
        email = self.cleaned_data.get("email")

        if not email:
            raise forms.ValidationError(_("E-mail is required."))

        try:
            User.objects.get(email=email)
            raise forms.ValidationError(_("That e-mail is already used."))
        except User.DoesNotExist:
            try:
                EmailValidation.objects.get(email=email)
                raise forms.ValidationError(_("That e-mail is already "
                                              "being confirmed."))
            except EmailValidation.DoesNotExist:
                return email

    def clean(self):
        """
        Verify that the 2 passwords fields are equal
        """
        if self.cleaned_data.get("password1") == \
           self.cleaned_data.get("password2"):
            return self.cleaned_data
        else:
            raise forms.ValidationError(_("The passwords inserted are different."))

class SignupForm(UserCreationForm):
    """
    Form for registering a new user userprofile.
    """
    email = forms.EmailField(label='Email address', max_length=75)
    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_email(self):
        """
        Verify that the email exists
        """
        email = self.cleaned_data.get("email")

        if not email:
            raise forms.ValidationError(_("E-MAIL IS REQUIRED"))

        try:
            User.objects.get(email=email)
            raise forms.ValidationError(_("THAT E-MAIL IS ALREADY USED"))
        except User.DoesNotExist:
            try:
                EmailValidation.objects.get(email=email)
                raise forms.ValidationError(_("THAT E-MAIL IS ALREADY CONFIRMED"))
            except EmailValidation.DoesNotExist:
                return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError(_("USERNAME IS REQUIRED"))
        try:
            User.objects.get(username=username)
            raise forms.ValidationError(_("THAT USERNAME IS ALREADY USED"))
        except:
            return username

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if not password1:
            raise forms.ValidationError(_("PASSWORD IS REQUIRED"))
        return password1

    def clean_password2(self):
        password2 = self.cleaned_data.get('password2')
        if not password2:
            raise forms.ValidationError(_("PASSWORD IS REQUIRED"))
        if not password2 == self.cleaned_data.get('password1'):
            raise forms.ValidationError(_("PASSWORDS ARE MISMATCH"))
        return password2


class LoginForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'password')
        widgets = dict(password=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if not user.is_active:
                raise forms.ValidationError(_("The user is disabled."))
            return self.cleaned_data
        else:
            raise forms.ValidationError(_("Incorrect login."))

class SigninForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'password')
        widgets = dict(password=forms.PasswordInput)

    def clean_email(self):
        username = self.cleaned_data["username"]
        if not username:
            raise forms.ValidationError("THIS FIELD IS REQUIRED")
        try:
            user = User.objects.get(username=username)
            if not user.is_active:
                raise forms.ValidationError(_("THE USER IS DISABLED"))
            self.auth_method = 'username'
            return username
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=username)
                if not user.is_active:
                    raise forms.ValidationError(_("THE USER IS DISABLED"))
                self.auth_method = 'email'
                return username
            except:
                raise forms.ValidationError("THIS EMAIL IS NOT REGISTERED")

        except User.DoesNotExist:
            raise forms.ValidationError("THIS EMAIL IS NOT REGISTERED")

    def clean_password(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(username=email, password=password)
        if not user:
            raise forms.ValidationError(_("THIS PASSWORD IS INCORRECT"))
        return password

class PassChangeForm(forms.Form):
    old_password = forms.CharField(label=_("Old password"), widget=forms.PasswordInput)
    new_password1 = forms.CharField(label=_("New password"), widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=_("New password confirmation"), widget=forms.PasswordInput)

    class Meta:
        fields = ('old_password', 'new_password1', 'new_password2')

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('user')
        super(PassChangeForm, self).__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data["old_password"]
        if not self.current_user.check_password(old_password):
            raise forms.ValidationError(_("Old password is wrong."))
        return old_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_("Passwords mismatch."))
        return password2

    def clean(self):
        if  self.cleaned_data.get('old_password') == self.cleaned_data.get('new_password2'):
            raise forms.ValidationError(_("Old and new passwords are equal."))
        return self.cleaned_data


class AvatarForm(forms.ModelForm):
    """
    The avatar form requires only one image field.
    """
    class Meta:
        model = Profile
        fields = ('avatar',)

    def clean(self):
        if not (self.cleaned_data.get('avatar')):
            raise forms.ValidationError(_('You must enter one of the options'))
        return self.cleaned_data




class AvatarCropForm(forms.ModelForm):
    """
    Crop dimensions form
    """
    top = forms.IntegerField()
    left = forms.IntegerField()
    right = forms.IntegerField()
    bottom = forms.IntegerField()

    class Meta:
        model = Profile
        fields = ('top','left','right','bottom')

    def clean(self):
        if int(self.cleaned_data.get('right')) - int(self.cleaned_data.get('left')) < 4:
            raise forms.ValidationError(_("You must select a portion of the image with a minimum of 4x4 pixels."))
        else:
            return self.cleaned_data


class EmailValidationForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        """
        Verify that the email exists
        """
        email = self.cleaned_data.get("email")
        if not (User.objects.filter(email=email) or
                EmailValidation.objects.filter(email=email)):
            return email

        raise forms.ValidationError(_("That e-mail is already used."))


class ResendEmailValidationForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        """
        Verify that the email exists
        """
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email) or \
           EmailValidation.objects.filter(email=email):
            return email

        raise forms.ValidationError(_("That e-mail isn't registered."))


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(label=_(u'First name'), max_length=30)
    last_name = forms.CharField(label=_(u'Last Name'), max_length=30)
    email = forms.EmailField(label=_("Site-only email"))
    birthdate = forms.DateField(('%d/%m/%Y',), label='Birth Date', required=False,
        widget=forms.DateTimeInput(format='%d/%m/%Y', attrs={
            'class': 'datePicker',
            'readonly': 'readonly',
            'size': '15'
            }))

    class Meta:
        model = Profile
        fields = (
            'first_name', 'last_name', 'email', 'gender', 'birthdate',
            'website', 'icq', 'skype', 'jabber', 'mobile', 'workphone',
            'facebook','googleplus','twitter',
            'publicmail', 'signature', 'time_zone', 'show_signatures', 'about')

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.get('instance', None)
        initial = {'first_name': self.profile.user.first_name,
                   'last_name': self.profile.user.last_name,
                   'email': self.profile.user.email}
        kwargs['initial'] = initial
        super(ProfileForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        f = super(ProfileForm, self).save(commit=False)
        if commit:
            f.save()
            self.profile.user.first_name = self.cleaned_data['first_name']
            self.profile.user.last_name = self.cleaned_data['last_name']
            self.profile.user.email = self.cleaned_data['email']
            self.profile.user.save()
        return f

class UserSettingsForm(forms.ModelForm):
    oldpassword = forms.CharField(label=_(u'Old Password'), max_length=30, required=False)
    newpassword = forms.CharField(label=_(u'New Password'), max_length=30, required=False)

    class Meta:
        model = Profile
        fields = (
            'fullname', 'publicmail', 'location', 'website',
            'facebook','googleplus','twitter', 'about', 'oldpassword', 'newpassword', 'subscribe')


class EditForm(forms.ModelForm):
    """Form for editing user userprofile"""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
