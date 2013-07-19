# -*- coding: utf-8 -*-
import os

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms.widgets import RadioSelect
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _

from nnmware.core.fields import ReCaptchaField
from nnmware.core.models import Pic, Tag, Doc, EmailValidation, Video
from nnmware.core.utils import tags_normalize
from nnmware.core.exceptions import UserIsDisabled


class TagsMixinForm(forms.ModelForm):
    tags = forms.CharField(label=_('Tags'))  # widget=AutocompleteWidget(choices_url='autocomplete_tags'))

    def clean_tags(self):
        """
        Convert tags in string and check max number of tags for object
        If not found - make new tag
        """
        tags = set(tags_normalize(self.cleaned_data.get("tags")))
        if len(tags) > settings.TAGS_MAX:
            raise forms.ValidationError(_("Max number or tags - %s.") % settings.TAGS_MAX)
        alltags = Tag.objects.filter(name__in=tags).values_list('name', flat=True)
        for tag in tags:
            if tag not in alltags:
                Tag(name=tag).save()
        return tags


class DocForm(forms.ModelForm):
    class Meta(object):
        model = Doc
        fields = ('file', 'description', 'created_date', 'locked', 'filetype')


class DocDeleteForm(forms.ModelForm):
    class Meta(object):
        model = Doc
        fields = ()


EDITOR_ACTION = (('rotate90', _('Rotate 90')), ('rotate270', _('Rotate 270')),
                 ('resize', _('Resize')))


class PicEditorForm(forms.ModelForm):
    """
    Crop dimensions form
    """
    top = forms.IntegerField()
    left = forms.IntegerField()
    right = forms.IntegerField()
    bottom = forms.IntegerField()
    editor_action = forms.ChoiceField(widget=RadioSelect, choices=EDITOR_ACTION)


class UploadPicForm(forms.Form):
    pic = forms.ImageField()

    def __init__(self, *args, **kwargs):
        kwargs.pop('size', settings.PIC_DEFAULT_SIZE)
        super(UploadPicForm, self).__init__(*args, **kwargs)

    def clean_pic(self):
        data = self.cleaned_data['pic']
        if settings.PIC_ALLOWED_FILE_EXTS:
            (root, ext) = os.path.splitext(data.name.lower())
            if ext not in settings.PIC_ALLOWED_FILE_EXTS:
                raise forms.ValidationError(
                    _("%(ext)s is an invalid file extension. "
                      "Authorized extensions are : %(valid_exts_list)s") %
                    {'ext': ext,
                     'valid_exts_list': ", ".join(settings.PIC_ALLOWED_FILE_EXTS)})
        if data.size > settings.PIC_MAX_SIZE:
            raise forms.ValidationError(
                _("Your file is too big (%(size)s), "
                  "the maximum allowed size is %(max_valid_size)s") %
                {'size': filesizeformat(data.size),
                 'max_valid_size': filesizeformat(settings.AVATAR_MAX_SIZE)})
        count = Pic.objects.for_object(self.target).count()
        if count >= settings.PIC_MAX_PER_OBJECT > 1:
            raise forms.ValidationError(
                _("You already have %(nb_pic)d image, and the "
                  "maximum allowed is %(nb_max_pic)d.") %
                {'nb_pic': count, 'nb_max_pic': settings.PIC_MAX_PER_OBJECT})
        return


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
            raise forms.ValidationError(_("E-MAIL IS REQUIRED"))
        try:
            get_user_model().objects.get(email=email)
            raise forms.ValidationError(_("THAT E-MAIL IS ALREADY USED"))
        except:
            return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError(_("PASSWORD IS REQUIRED"))
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
        if self.cleaned_data.get('old_password') == self.cleaned_data.get('new_password2'):
            raise forms.ValidationError(_("Old and new passwords are equal."))
        return self.cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(label=_('Username'), max_length=30)
    password = forms.CharField(label=_('Password'), max_length=30)

    class Meta:
        widgets = dict(password=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if not username:
            raise forms.ValidationError(_("THIS FIELD IS REQUIRED"))
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
                raise forms.ValidationError(_("THIS EMAIL IS NOT REGISTERED"))
        except UserIsDisabled:
            raise forms.ValidationError(_("THE USER IS DISABLED"))

    def clean_password(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError(_("THIS PASSWORD IS INCORRECT"))
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
            raise forms.ValidationError(_("E-mail is required."))

        try:
            get_user_model().objects.get(email=email)
            raise forms.ValidationError(_("That e-mail is already used."))
        except get_user_model().DoesNotExist:
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

    class Meta:
        model = get_user_model()
        fields = ('username', 'email')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError(_("USERNAME IS REQUIRED"))
        try:
            get_user_model().objects.get(username=username)
            raise forms.ValidationError(_("THAT USERNAME IS ALREADY USED"))
        except:
            return username

    def clean_email(self):
        """
        Verify that the email exists
/        """
        email = self.cleaned_data.get("email")

        if not email:
            raise forms.ValidationError(_("E-MAIL IS REQUIRED"))

        try:
            get_user_model().objects.get(email=email)
            raise forms.ValidationError(_("THAT E-MAIL IS ALREADY USED"))
        except get_user_model().DoesNotExist:
            try:
                EmailValidation.objects.get(email=email)
                raise forms.ValidationError(_("THAT E-MAIL IS ALREADY CONFIRMED"))
            except EmailValidation.DoesNotExist:
                return email

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
            raise forms.ValidationError(_("You must select a portion of the image with a minimum of 4x4 pixels."))
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
            raise forms.ValidationError(_('You must enter one of the options'))
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

        raise forms.ValidationError(_("That e-mail is already used."))


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

        raise forms.ValidationError(_("That e-mail isn't registered."))


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


class CoreUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()

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
