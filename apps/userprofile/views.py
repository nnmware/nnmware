import os
import Image
import json
from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, SiteProfileNotAvailable

from django.contrib.auth.forms import PasswordResetForm, AuthenticationForm, \
    PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, \
    HttpResponseForbidden, Http404
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.views.generic.base import View, TemplateView
from django.views.generic import FormView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from django.views.generic import YearArchiveView, MonthArchiveView, \
    DayArchiveView
from nnmware.core.ajax import AjaxLazyAnswer
from nnmware.core.imgutil import resize_image, remove_thumbnails, remove_file
from nnmware.core.utils import make_key, send_template_mail
from nnmware.core.views import AjaxFormMixin

from nnmware.apps.userprofile.models import Profile, EmailValidation
from nnmware.apps.userprofile.forms import *
from nnmware.core.imgutil import fit


class UserList(ListView):
    model = User
    context_object_name = "object_list"
    template_name = "user/users_list.html"

    def get_queryset(self):
        return User.objects.order_by("-date_joined")


class UserMenList(UserList):
    def get_queryset(self):
        return User.objects.filter(profile__gender='M')


class UserWomenList(UserList):
    def get_queryset(self):
        return User.objects.filter(profile__gender='F')


class UserDateTemplate(object):
    template_name = 'user/users_list.html'
    model = User
    date_field = 'date_joined'
    context_object_name = "object_list"
    make_object_list = True
    allow_empty = True


class UserYearList(UserDateTemplate, YearArchiveView):
    pass


class UserMonthList(UserDateTemplate, MonthArchiveView):
    pass


class UserDayList(UserDateTemplate, DayArchiveView):
    pass


class UserDetail(DetailView):
    model = User
    slug_field = 'username'
    template_name = "user/user_detail.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(UserDetail,self).get_context_data(**kwargs)
        context['ctype'] = ContentType.objects.get_for_model(User)
        return context



class ProfileEdit(AjaxFormMixin, UpdateView):
    form_class = ProfileForm
    template_name = "user/profile_edit.html"

    def get_object(self, queryset=None):
        return self.request.user.get_profile()

    def get_success_url(self):
        return reverse('user_detail', args=[self.request.user.username])

class AvatarEdit(UpdateView):
    model = Profile
    form_class = AvatarForm
    template_name = "user/settings.html"
    success_url = reverse_lazy('user_settings')

    def form_valid(self, form):
        avatar_path = self.object.avatar.url
        remove_thumbnails(avatar_path)
        remove_file(avatar_path)
        self.object = form.save(commit=False)
        self.object.avatar_complete = False
        self.object.save()
        resize_image(self.object.avatar.url)
        return super(AvatarEdit, self).form_valid(form)

    def get_object(self, queryset=None):
        return self.request.user.get_profile()


class AvatarCrop(UpdateView):
    form_class = AvatarCropForm
    template_name = "user/settings.html"
    success_url = reverse_lazy('user_settings')

    def get_object(self, queryset=None):
        return self.request.user.get_profile()

    def form_valid(self, form):
        top = int(form.cleaned_data.get('top'))
        left = int(form.cleaned_data.get('left'))
        right = int(form.cleaned_data.get('right'))
        bottom = int(form.cleaned_data.get('bottom'))
        image = Image.open(self.object.avatar.path)
        box = [left, top, right, bottom]
        image = image.crop(box)
        if image.mode not in ('L', 'RGB'):
            image = image.convert('RGB')
        image = fit(image, 120)
        image.save(self.object.avatar.path)
        self.object.avatar_complete = True
        self.object.save()
        return super(AvatarCrop, self).form_valid(form)


class UserSettings(UpdateView):
    form_class = UserSettingsForm
    template_name = "user/settings.html"

    def get_object(self, queryset=None):
        return self.request.user.get_profile()

    def get_success_url(self):
        return reverse('user_detail', args=[self.request.user.username])



class UserSearch(ListView):
    model = User
    template_name = "user/users_list.html"

    def get_queryset(self):
        query = self.request.GET.get('q')
        return User.objects.filter(username__icontains=query)


class RegisterView(AjaxFormMixin, FormView):
    form_class = RegistrationForm
    template_name = 'user/registration.html'
    success_url = "/users"
    status = _("YOU GOT ON E-MAIL IS CONFIRMATION. CHECK EMAIL")


    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        email = form.cleaned_data.get('email')
        newuser = User.objects.create_user(username=username, email=email, password=password)
        newuser.is_active = False
        EmailValidation.objects.add(user=newuser, email=newuser.email)
        newuser.save()
        return super(RegisterView, self).form_valid(form)

class SignupView(FormView):
    form_class = SignupForm
    template_name = 'registration/signup.html'
    success_url = "/"
    status = _("YOU GOT ON E-MAIL IS CONFIRMATION. CHECK EMAIL")

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        try:
            e = EmailValidation.objects.get(email=email)
        except :
            e = EmailValidation()
            e.username = username
            e.email = email
            e.password = password
            e.created = datetime.now()
            e.key = make_key(username)
            e.save()
        mail_dict = {'key': e.key,
                     'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                     'site_name': settings.SITENAME, 'email': email}
        subject = 'registration/activation_subject.txt'
        body = 'registration/activation.txt'
        send_template_mail(subject,body,mail_dict,[e.email])
        return super(SignupView, self).form_valid(form)

class SignupAjaxView(AjaxFormMixin, SignupView):
    pass

class LoginView(FormView):
    form_class = LoginForm
    template_name = 'user/login.html'
    success_url = "/"
    status = _("YOU SUCCESSFULLY SIGN IN")

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        raise
        login(self.request, user)
        return super(LoginView, self).form_valid(form)

class LoginAjaxView(AjaxFormMixin, LoginView):
    pass

class ChangePasswordView(AjaxFormMixin, FormView):
    form_class = PassChangeForm
    template_name = 'user/pwd_change.html'
    success_url = reverse_lazy('password_change_done')

    def get_form_kwargs(self):
        kwargs = super(ChangePasswordView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        self.request.user.set_password(form.cleaned_data.get('new_password2'))
        self.request.user.save()
        return super(ChangePasswordView, self).form_valid(form)


class LogoutView(TemplateView):
    template_name = 'user/logged_out.html'

    def get(self, request, *args, **kwargs):
        logout(self.request)
        return super(LogoutView, self).get(request, *args, **kwargs)

class ActivateView(View):
    template_name = 'user/logged_out.html'

    def get(self, request, *args, **kwargs):
        key = self.kwargs['activation_key']
        try:
            e = EmailValidation.objects.get(key=key)
            u = User(username=e.username,email=e.email)
            u.set_password(e.password)
            u.is_active = True
            u.save()
            e.delete()
            user = authenticate(username=e.username, password=e.password)
            login(self.request, user)
        except :
            raise Http404
        return HttpResponseRedirect(reverse('user_profile', args=[user.pk]))

class PassRecoveryView(View):
    template_name = 'user/logged_out.html'

    def get(self, request, *args, **kwargs):
        key = self.kwargs['activation_key']
        try:
            e = EmailValidation.objects.get(key=key)
            u = User.objects.get(username=e.username)
            u.set_password(e.password)
            u.save()
            user = authenticate(username=u.username, password=e.password)
            e.delete()
            login(self.request, user)
        except :
            raise Http404
        return HttpResponseRedirect(reverse('user_profile', args=[user.pk]))


@login_required
def avatardelete(request):
    if request.is_ajax():
        try:
            profile = request.user.get_profile()
            remove_thumbnails(profile.avatar.path)
            remove_file(profile.avatar.path)
            profile.avatar_complete = False
            profile.avatar = None
            profile.save()
            payload = {'success': True}
        except:
            payload = {'success': False}
        return AjaxLazyAnswer(payload)
    else:
        raise Http404()
