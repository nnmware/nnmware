# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import ugettext_lazy as _

from nnmware.core.fields import ReCaptchaField
from nnmware.core.models import Tag, EmailValidation, Video
from nnmware.core.utils import tags_normalize, setting
from nnmware.core.exceptions import UserIsDisabled

TAGS_MAX = setting('TAGS_MAX', 10)


class TagsMixinForm(forms.ModelForm):
    tags = forms.CharField(label=_('Tags'))  # widget=AutocompleteWidget(choices_url='autocomplete_tags'))

    def clean_tags(self):
        """
        Convert tags in string and check max number of tags for object
        If not found - make new tag
        """
        tags = set(tags_normalize(self.cleaned_data.get("tags")))
        if len(tags) > TAGS_MAX:
            raise forms.ValidationError(_("Max number or tags - %s.") % TAGS_MAX)
        alltags = Tag.objects.filter(name__in=tags).values_list('name', flat=True)
        for tag in tags:
            if tag not in alltags:
                Tag(name=tag).save()
        return tags


class EmailQuickRegisterForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'password')

    def clean_email(self):
        """
        Verify that the email exists
        """
        email = self.cleaned_data.get("email")
        if not email:
            raise forms.ValidationError(_("E-MAIL IS REQUIRED"), code='invalid')
        try:
            get_user_model().objects.get(email=email)
            raise forms.ValidationError(_("THAT E-MAIL IS ALREADY USED"), code='invalid')
        except:
            return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError(_("PASSWORD IS REQUIRED"), code='invalid')
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
            raise forms.ValidationError(_("Old password is wrong."), code='invalid')
        return old_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_("Passwords mismatch."), code='invalid')
        return password2

    def clean(self):
        if self.cleaned_data.get('old_password') == self.cleaned_data.get('new_password2'):
            raise forms.ValidationError(_("Old and new passwords are equal."), code='invalid')
        return self.cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(label=_('Username'), max_length=30)
    password = forms.CharField(label=_('Password'), max_length=30)

    class Meta:
        widgets = dict(password=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if not username:
            raise forms.ValidationError(_("THIS FIELD IS REQUIRED"), code='invalid')
        try:
            user = get_user_model().objects.get(username=username)
            if not user.is_active:
                raise UserIsDisabled
            return username
        except get_user_model().DoesNotExist:
            try:
                user = get_user_model().objects.get(email=username)
                if not user.is_active:
                    raise UserIsDisabled
                return username
            except UserIsDisabled:
                raise UserIsDisabled
            except:
                raise forms.ValidationError(_("THIS EMAIL IS NOT REGISTERED"), code='invalid')
        except UserIsDisabled:
            raise forms.ValidationError(_("THE USER IS DISABLED"), code='invalid')

    def clean_password(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError(_("THIS PASSWORD IS INCORRECT"), code='invalid')
        return password


class UserSettingsForm(forms.ModelForm):
    oldpassword = forms.CharField(label=_('Old Password'), max_length=30, required=False)
    newpassword = forms.CharField(label=_('New Password'), max_length=30, required=False)

    class Meta:
        model = get_user_model()
        fields = ('oldpassword', 'newpassword')

#            'fullname', 'publicmail', 'location', 'website',
#            'facebook','googleplus','twitter', 'about', 'oldpassword', 'newpassword', 'subscribe')


class RegistrationForm(UserCreationForm):
    """
    Form for registering a new user userprofile.
    """

    class Meta:
        model = get_user_model()
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        if settings.CAPTCHA_ENABLED:
            self.fields['recaptcha'] = ReCaptchaField(error_messages={'required': _('This field is required'),
                                                                      'invalid': _('Answer is wrong')})
        super(RegistrationForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        """
        Verify that the email exists
        """
        email = self.cleaned_data.get("email")

        if not email:
            raise forms.ValidationError(_("E-mail is required."), code='invalid')

        try:
            get_user_model().objects.get(email=email)
            raise forms.ValidationError(_("That e-mail is already used."), code='invalid')
        except get_user_model().DoesNotExist:
            try:
                EmailValidation.objects.get(email=email)
                raise forms.ValidationError(_("That e-mail is already being confirmed."), code='invalid')
            except EmailValidation.DoesNotExist:
                return email

    def clean(self):
        """
        Verify that the 2 passwords fields are equal
        """
        if self.cleaned_data.get("password1") == self.cleaned_data.get("password2"):
            return self.cleaned_data
        else:
            raise forms.ValidationError(_("The passwords inserted are different."), code='invalid')


class SignupForm(UserCreationForm):
    """
    Form for registering a new user userprofile.
    """

    class Meta:
        model = get_user_model()
        fields = ('username', 'email')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError(_("USERNAME IS REQUIRED"), code='invalid')
        try:
            get_user_model().objects.get(username=username)
            raise forms.ValidationError(_("THAT USERNAME IS ALREADY USED"), code='invalid')
        except:
            return username

    def clean_email(self):
        """
        Verify that the email exists
/        """
        email = self.cleaned_data.get("email")

        if not email:
            raise forms.ValidationError(_("E-MAIL IS REQUIRED"), code='invalid')

        try:
            get_user_model().objects.get(email=email)
            raise forms.ValidationError(_("THAT E-MAIL IS ALREADY USED"), code='invalid')
        except get_user_model().DoesNotExist:
            try:
                EmailValidation.objects.get(email=email)
                raise forms.ValidationError(_("THAT E-MAIL IS ALREADY CONFIRMED"), code='invalid')
            except EmailValidation.DoesNotExist:
                return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if not password1:
            raise forms.ValidationError(_("PASSWORD IS REQUIRED"), code='invalid')
        return password1

    def clean_password2(self):
        password2 = self.cleaned_data.get('password2')
        if not password2:
            raise forms.ValidationError(_("PASSWORD IS REQUIRED"), code='invalid')
        if not password2 == self.cleaned_data.get('password1'):
            raise forms.ValidationError(_("PASSWORDS ARE MISMATCH"), code='invalid')
        return password2


class AvatarCropForm(forms.ModelForm):
    """
    Crop dimensions form
    """
    top = forms.IntegerField()
    left = forms.IntegerField()
    right = forms.IntegerField()
    bottom = forms.IntegerField()

    class Meta:
        model = get_user_model()
        fields = ('top', 'left', 'right', 'bottom')

    def clean(self):
        if int(self.cleaned_data.get('right')) - int(self.cleaned_data.get('left')) < 4:
            raise forms.ValidationError(_("You must select a portion of the image with a minimum of 4x4 pixels."),
                                        code='invalid')
        else:
            return self.cleaned_data


class AvatarForm(forms.ModelForm):
    """
    The avatar form requires only one image field.
    """

    class Meta:
        model = get_user_model()
        fields = ('img',)

    def clean(self):
        if not (self.cleaned_data.get('img')):
            raise forms.ValidationError(_('You must enter one of the options'), code='invalid')
        return self.cleaned_data


class EmailValidationForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        """
        Verify that the email exists
        """
        email = self.cleaned_data.get("email")
        if not (get_user_model().objects.filter(email=email) or EmailValidation.objects.filter(email=email)):
            return email

        raise forms.ValidationError(_("That e-mail is already used."), code='invalid')


class ResendEmailValidationForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        """
        Verify that the email exists
        """
        email = self.cleaned_data.get("email")
        if get_user_model().objects.filter(email=email) or \
                EmailValidation.objects.filter(email=email):
            return email

        raise forms.ValidationError(_("That e-mail isn't registered."), code='invalid')


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(label=_('First name'), max_length=30)
    last_name = forms.CharField(label=_('Last Name'), max_length=30)
    email = forms.EmailField(label=_("Site-only email"))
    birthdate = forms.DateField(('%d/%m/%Y',), label='Birth Date', required=False,
                                widget=forms.DateTimeInput(format='%d/%m/%Y', attrs={
                                    'class': 'datePicker',
                                    'readonly': 'readonly',
                                    'size': '15'
                                }))

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email', 'birthdate')
    #            'first_name', 'last_name', 'email', 'gender', 'birthdate',
    #            'website', 'icq', 'skype', 'jabber', 'mobile', 'workphone',
    #            'facebook','googleplus','twitter',
    #            'publicmail', 'signature', 'time_zone', 'show_signatures', 'about')

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


class EditForm(forms.ModelForm):
    """Form for editing user userprofile"""

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email')


class VideoAddForm(TagsMixinForm):
    class Meta:
        model = Video
        fields = ('project_url', 'project_name', 'video_url', 'tags', 'description')
        widgets = dict(description=forms.Textarea)


class CoreUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = '__all__'


class CoreUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = '__all__'

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])


class UserFromRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(UserFromRequestForm, self).__init__(*args, **kwargs)
        self._user = user


class CategoryMixinForm(forms.ModelForm):

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if not category:
            raise forms.ValidationError(_('Category is required'), code='invalid')
        return category


class NameMixinForm(forms.ModelForm):

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name is None or len(name.strip()) == 0:
            raise forms.ValidationError(_('Name is required'), code='invalid')
        return name


class DescriptionMixinForm(forms.ModelForm):

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description is None or len(description.strip()) == 0:
            raise forms.ValidationError(_('Description is required'), code='invalid')
        return description
