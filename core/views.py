# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import json
from PIL import Image
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.db.models.aggregates import Sum
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateResponseMixin, TemplateView, View
from django.views.generic.dates import YearArchiveView, MonthArchiveView, DayArchiveView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import UpdateView, BaseFormView, FormMixin, DeleteView, FormView
from django.views.generic.list import ListView
from django.utils.translation import ugettext_lazy as _
from nnmware.core import oembed
from nnmware.core.backends import image_from_url
from nnmware.core.decorators import ssl_required, ssl_not_required
from nnmware.core.ajax import as_json, AjaxLazyAnswer
from nnmware.core.http import LazyEncoder
from nnmware.core.imgutil import remove_thumbnails, remove_file, resize_image, fit
from nnmware.core.models import Nnmcomment, Doc, Pic, Follow, Notice, Message, Action, EmailValidation, ACTION_ADDED
from nnmware.core.forms import *
from nnmware.core.signals import action
from nnmware.core.utils import send_template_mail, make_key, get_oembed_end_point, get_video_provider_from_link, \
    gen_shortcut, update_video_size


class UserPathMixin(object):
    def get_object(self, queryset=None):
        return get_object_or_404(get_user_model(), username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        kwargs['object'] = self.object
        return super(UserPathMixin, self).get_context_data(**kwargs)


class UserToFormMixin(object):
    def get_form_kwargs(self):
        kwargs = super(UserToFormMixin, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class AjaxFormMixin(object):
    def form_valid(self, form):
        if self.request.is_ajax():
            self.success = True
            payload = dict(success=self.success, location=self.success_url or self.get_success_url())
            try:
                payload['status_msg'] = self.status_msg
            except:
                pass
            return AjaxLazyAnswer(payload)
        else:
            return HttpResponseRedirect(self.success_url)

    def form_invalid(self, form, *args, **kwargs):
        self.data = as_json(form.errors)
        self.success = False

        payload = {'success': self.success, 'data': self.data}

        if self.request.is_ajax():
            return AjaxLazyAnswer(payload)
        else:
            return super(AjaxFormMixin, self).form_invalid(form, *args, **kwargs)


class AjaxViewMixin(View):
    """
    A mixin that can be used to render a JSON response for CBV.
    """
    payload = {}

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            html = render_to_string(self.template_name, context, context_instance=RequestContext(self.request))
            payload = {'success': True, 'html': html}
            payload.update(self.payload)
            response_kwargs['content_type'] = 'application/json'
            return HttpResponse(json.dumps(payload, cls=LazyEncoder), **response_kwargs)
        return super(AjaxViewMixin, self).render_to_response(context, **response_kwargs)


class DocEdit(UpdateView):
    model = Doc
    form_class = DocForm
    template_name = "upload/doc_form.html"

    def get_success_url(self):
        return self.object.content_object.get_absolute_url()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DocEdit, self).get_context_data(**kwargs)
        context['action'] = reverse("doc_edit", args=[self.object.id])
        return context


class DocDelete(DeleteView):
    model = Doc
    #form_class = JDocDeleteForm
    template_name = "upload/doc_delete.html"

    def get_success_url(self):
        return self.object.content_object.get_absolute_url()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DocDelete, self).get_context_data(**kwargs)
        context['action'] = reverse("doc_del", args=[self.object.id])
        return context


class PicDelete(DeleteView):
    model = Pic
    template_name = "upload/pic_delete.html"

    def get_success_url(self):
        return self.object.content_object.get_absolute_url()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PicDelete, self).get_context_data(**kwargs)
        context['action'] = reverse("pic_del", args=[self.object.id])
        return context


class PicView(DetailView):
    model = Pic
    template_name = "upload/pic_view.html"

    def get_context_data(self, **kwargs):
        context = super(PicView, self).get_context_data(**kwargs)
        context['pic'] = self.object.pic.url
        return context


class PicEditor(UpdateView):
    model = Pic
    form_class = PicEditorForm
    template_name = "upload/pic_editor.html"

    def get_success_url(self):
        return self.object.content_object.get_absolute_url()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PicEditor, self).get_context_data(**kwargs)
        context['action'] = reverse("pic_editor", args=[self.object.id])
        return context

    def form_valid(self, form):
        action = form.cleaned_data.get('editor_action')
        if action == 'resize':
            top = int(form.cleaned_data.get('top'))
            left = int(form.cleaned_data.get('left'))
            right = int(form.cleaned_data.get('right'))
            bottom = int(form.cleaned_data.get('bottom'))
            if not (top - bottom) or not (left - right):
                return super(PicEditor, self).form_valid(form)
            image = Image.open(self.object.pic.path)
            box = [left, top, right, bottom]
            image = image.crop(box)
            if image.mode not in ('L', 'RGB'):
                image = image.convert('RGB')
            image.save(self.object.pic.path)
        elif action == 'rotate90':
            image = Image.open(self.object.pic.path)
            image = image.rotate(90)
            if image.mode not in ('L', 'RGB'):
                image = image.convert('RGB')
            image.save(self.object.pic.path)
        elif action == 'rotate270':
            image = Image.open(self.object.pic.path)
            image = image.rotate(270)
            if image.mode not in ('L', 'RGB'):
                image = image.convert('RGB')
            image.save(self.object.pic.path)

        remove_thumbnails(self.object.pic.path)
        self.object.save()
        return super(PicEditor, self).form_valid(form)


class PicList(ListView):
    template_name = 'upload/pic_list.html'
    model = Pic


class PicYearList(YearArchiveView):
    template_name = 'upload/pic_list.html'
    model = Pic
    date_field = 'created_date'
    context_object_name = "object_list"
    make_object_list = True
    allow_empty = True


class PicMonthList(MonthArchiveView):
    template_name = 'upload/pic_list.html'
    model = Pic
    date_field = 'created_date'
    context_object_name = "object_list"
    make_object_list = True


class PicDayList(DayArchiveView):
    template_name = 'upload/pic_list.html'
    model = Pic
    date_field = 'created_date'
    context_object_name = "object_list"
    make_object_list = True


class DocList(ListView):
    template_name = 'upload/doc_list.html'
    model = Doc


class DocYearList(YearArchiveView):
    template_name = 'upload/doc_list.html'
    model = Doc
    date_field = 'created_date'
    context_object_name = "object_list"
    make_object_list = True
    allow_empty = True


class DocMonthList(MonthArchiveView):
    template_name = 'upload/doc_list.html'
    model = Doc
    date_field = 'created_date'
    context_object_name = "object_list"
    make_object_list = True


class DocDayList(DayArchiveView):
    template_name = 'upload/doc_list.html'
    model = Doc
    date_field = 'created_date'
    context_object_name = "object_list"
    make_object_list = True


class DocAdd(TemplateView):
    template_name = "upload/doc_upload.html"


class AddPicView(TemplateResponseMixin, BaseFormView):
    form_class = UploadPicForm
    template_name = "upload/pic_form.html"

    def create_pic(self, target, pic_file):
        img = Pic(content_object=target)
        img.pic.save(pic_file.name, pic_file)
        img.save()
        return img

    def form_valid(self, form):
        new_pic = self.create_pic(self.target, self.request.FILES['pic'])
        if new_pic:
            messages.info(self.request, _("Successfully uploaded a new image."))
        if self.request.is_ajax() or self.request.REQUEST.get('async', None) == 'true':
            return self.ajax_form_valid(new_pic)
        else:
            return FormMixin.form_valid(self, form)


class CurrentUserAuthor(object):
    """ Generic update view that check request.user is author of object """

    def dispatch(self, *args, **kwargs):
        response = super(CurrentUserAuthor, self).dispatch(*args, **kwargs)
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404
        return response


class CurrentUserAuthenticated(object):
    """ Generic update view that check request.user is author of object """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            raise Http404
        return super(CurrentUserAuthenticated, self).dispatch(request, *args, **kwargs)


class CurrentUserSuperuser(object):
    """ Generic object for view that check superuser rights for current user """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise Http404
        return super(CurrentUserSuperuser, self).dispatch(request, *args, **kwargs)


class CurrentUserEditor(object):
    """ Generic update view that checks permissions for change object """

    def dispatch(self, *args, **kwargs):
        if not self.request.user.has_perm('%s.change_%s' % (self.model._meta.app_label, self.model._meta.model_name)):
            raise Http404
        return super(CurrentUserEditor, self).dispatch(*args, **kwargs)


class CurrentUserCreator(object):
    """ Generic create view that checks permissions """

    def dispatch(self, *args, **kwargs):
        if not self.request.user.has_perm('%s.create_%s' % (self.model._meta.app_label, self.model._meta.model_name)):
            raise Http404
        return super(CurrentUserCreator, self).dispatch(*args, **kwargs)


class AttachedImagesMixin(object):
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(AttachedImagesMixin, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the images
        pics = Pic.objects.for_object(self.object)
        pics_size = pics.aggregate(Sum('size'))['size__sum']
        context['pics'] = pics
        context['pics_size'] = pics_size
        return context


class AttachedFilesMixin(object):
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(AttachedFilesMixin, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the docs and files
        docs = Doc.objects.for_object(self.object)
        docs_size = docs.aggregate(Sum('size'))['size__sum']
        context['docs'] = docs
        context['docs_size'] = docs_size
        return context


class AttachedMixin(AttachedFilesMixin, AttachedImagesMixin):
    pass


class TagDetail(DetailView):
    model = Tag
    slug_field = 'slug'
    template_name = "tag/detail.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TagDetail, self).get_context_data(**kwargs)
        context['tab'] = 'all'
        context['ctype'] = ContentType.objects.get_for_model(Tag)
        return context


class TagsView(ListView):
    paginate_by = 20
    template_name = 'tag/tags_list.html'
    model = Tag

    def get_object(self):
        return Tag.objects.order_by('name')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TagsView, self).get_context_data(**kwargs)
        context['tab'] = 'popular_tags'
        context['tab_message'] = 'ALL SITE TAGS:'
        return context


class TagsPopularView(ListView):
    # Popular Tags limit 20
    template_name = 'tag/popular.html'
    model = Tag
    queryset = sorted(Tag.objects.order_by('-follow')[:20], key=lambda o: o.name)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TagsPopularView, self).get_context_data(**kwargs)
        context['tab'] = 'popular_tags'
        context['tab_message'] = '20 OF MOST POPULAR TAGS:'
        return context


class TagsCloudView(ListView):
    template_name = 'tag/tags_cloud.html'
    model = Tag


class TagsLetterView(ListView):
    template_name = 'tag/tags_list.html'
    model = Tag

    def get_queryset(self):
        return Tag.objects.filter(name__startswith=self.kwargs['letter'])


class NoticeView(ListView):
    paginate_by = 20
    template_name = 'notice/list.html'
    model = Notice

    def get_queryset(self):
        return Notice.objects.filter(user=self.request.user).order_by('-timestamp')


class MessagesView(UserPathMixin, SingleObjectMixin, ListView):
    paginate_by = 20
    model = Message
    template_name = "messages/list.html"
    context_object_name = "object_list"
    make_object_list = True

    def get_queryset(self):
        self.object = self.get_object()
        result = Message.objects.concrete_user(self.request.user, self.object)
        answ = result.filter(recipient=self.request.user).update(read_at=datetime.now())
        return result

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        kwargs['object'] = self.object
        context = super(MessagesView, self).get_context_data(**kwargs)
        return context


class MessageContactsView(ListView):
    paginate_by = 20
    model = Message
    template_name = "messages/userlist.html"
    #    context_object_name = "object_list"
    make_object_list = True

    def get_queryset(self):
        return Message.objects.users(self.request.user)


class RedirectHttpsView(object):
    @method_decorator(ssl_required)
    def dispatch(self, request, *args, **kwargs):
        return super(RedirectHttpsView, self).dispatch(request, *args, **kwargs)


class RedirectHttpView(object):
    @method_decorator(ssl_not_required)
    def dispatch(self, request, *args, **kwargs):
        return super(RedirectHttpView, self).dispatch(request, *args, **kwargs)


class ChangePasswordView(AjaxFormMixin, FormView):
    form_class = PassChangeForm
    template_name = 'user/pwd_change.html'
    success_url = reverse_lazy('password_change_done')

    def get_form_kwargs(self):
        kwargs = super(ChangePasswordView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        new_pw = form.cleaned_data.get('new_password2')
        self.request.user.set_password(new_pw)
        self.request.user.save()
        try:
            recipients = [self.request.user.email]
            mail_dict = {'new_pw': new_pw}
            subject = 'emails/changepass_client_subject.txt'
            body = 'emails/changepass_client_body.txt'
            send_template_mail(subject, body, mail_dict, recipients)
        except:
            pass
        return super(ChangePasswordView, self).form_valid(form)


class LoginView(AjaxFormMixin, FormView):
    form_class = LoginForm
    template_name = 'user/login.html'
    success_url = "/"
    status = _("YOU SUCCESSFULLY SIGN IN")

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return super(LoginView, self).form_valid(form)


class EmailQuickRegisterView(AjaxFormMixin, FormView):
    form_class = EmailQuickRegisterForm
    success_url = "/"

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        username = email
        password = form.cleaned_data.get('password')
        u = get_user_model()(username=username, email=email)
        u.set_password(password)
        u.is_active = True
        u.save()
        user = authenticate(username=username, password=password)
        self.user = user
        login(self.request, user)
        try:
            recipients = [email]
            mail_dict = {'name': email, 'pw': password}
            subject = 'emails/welcome_subject.txt'
            body = 'emails/welcome_body.txt'
            send_template_mail(subject, body, mail_dict, recipients)
        except:
            pass
        return super(EmailQuickRegisterView, self).form_valid(form)


class ActivateView(View):
    template_name = 'user/logged_out.html'

    def get_success_url(self):
        return reverse('user_profile', args=[self.user.username])

    def get(self, request, *args, **kwargs):
        key = self.kwargs['activation_key']
        try:
            e = EmailValidation.objects.get(key=key)
            u = get_user_model()(username=e.username, email=e.email)
            u.set_password(e.password)
            u.is_active = True
            u.save()
            e.delete()
            user = authenticate(username=e.username, password=e.password)
            self.user = user
            login(self.request, user)
        except:
            raise Http404
        return HttpResponseRedirect(self.get_success_url())


class PassRecoveryView(View):
    template_name = 'user/logged_out.html'

    def get(self, request, *args, **kwargs):
        key = self.kwargs['activation_key']
        try:
            e = EmailValidation.objects.get(key=key)
            u = get_user_model().objects.get(username=e.username)
            u.set_password(e.password)
            u.save()
            user = authenticate(username=u.username, password=e.password)
            e.delete()
            login(self.request, user)
        except:
            raise Http404
        return HttpResponseRedirect(reverse('user_profile', args=[user.username]))


class LogoutView(TemplateView):
    template_name = 'user/logged_out.html'

    def get(self, request, *args, **kwargs):
        logout(self.request)
        return super(LogoutView, self).get(request, *args, **kwargs)


class AjaxLogoutView(TemplateView):
    def post(self, request, *args, **kwargs):
        self.success = True
        location = None
        try:
            logout(self.request)
            location = '/'
        except:
            self.success = False
        payload = {'success': self.success, 'location': location}
        return AjaxLazyAnswer(payload)


class UserSettings(UpdateView):
    form_class = UserSettingsForm
    template_name = "user/settings.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('user_detail', args=[self.request.user.username])


class UserSearch(ListView):
    model = get_user_model()
    template_name = "user/users_list.html"

    def get_queryset(self):
        query = self.request.GET.get('q')
        return get_user_model().objects.filter(username__icontains=query)


class RegisterView(AjaxFormMixin, FormView):
    form_class = RegistrationForm
    template_name = 'user/registration.html'
    success_url = "/users"
    status = _("YOU GOT ON E-MAIL IS CONFIRMATION. CHECK EMAIL")

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        email = form.cleaned_data.get('email')
        newuser = get_user_model().objects.create_user(username=username, email=email, password=password)
        newuser.is_active = False
        EmailValidation.objects.add(user=newuser, email=newuser.email)
        newuser.save()
        return super(RegisterView, self).form_valid(form)


class SignupView(AjaxFormMixin, FormView):
    form_class = SignupForm
    template_name = 'registration/signup.html'
    success_url = "/"
    status = _("YOU GOT ON E-MAIL IS CONFIRMATION. CHECK EMAIL")

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password2')
        try:
            e = EmailValidation.objects.get(email=email)
        except:
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
        send_template_mail(subject, body, mail_dict, [e.email])
        return super(SignupView, self).form_valid(form)


class UserList(ListView):
    model = get_user_model()
    context_object_name = "object_list"
    template_name = "users/list.html"

    def get_queryset(self):
        return get_user_model().objects.order_by("-date_joined")


class UserMenList(UserList):
    def get_queryset(self):
        return get_user_model().objects.filter(gender='M')


class UserWomenList(UserList):
    def get_queryset(self):
        return get_user_model().objects.filter(gender='F')


class UserNoGenderList(UserList):
    def get_queryset(self):
        return get_user_model().objects.exclude(Q(gender='F') | Q(gender='M'))


class UserDateTemplate(object):
    template_name = 'users/list.html'
    model = get_user_model()
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
    model = get_user_model()
    slug_field = 'username'
    template_name = "user/user_detail.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(UserDetail, self).get_context_data(**kwargs)
        context['ctype'] = ContentType.objects.get_for_model(get_user_model())
        return context


class ProfileEdit(AjaxFormMixin, UpdateView):
    form_class = ProfileForm
    template_name = "user/profile_edit.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('user_detail', args=[self.request.user.username])


class AvatarEdit(UpdateView):
    model = get_user_model()
    form_class = AvatarForm
    template_name = "user/settings.html"
    success_url = reverse_lazy('user_settings')

    def form_valid(self, form):
        avatar_path = self.object.img.url
        remove_thumbnails(avatar_path)
        remove_file(avatar_path)
        self.object = form.save(commit=False)
        self.object.avatar_complete = False
        self.object.save()
        resize_image(self.object.img.url)
        return super(AvatarEdit, self).form_valid(form)

    def get_object(self, queryset=None):
        return self.request.user


class AvatarCrop(UpdateView):
    form_class = AvatarCropForm
    template_name = "user/settings.html"
    success_url = reverse_lazy('user_settings')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        top = int(form.cleaned_data.get('top'))
        left = int(form.cleaned_data.get('left'))
        right = int(form.cleaned_data.get('right'))
        bottom = int(form.cleaned_data.get('bottom'))
        image = Image.open(self.object.img.path)
        box = [left, top, right, bottom]
        image = image.crop(box)
        if image.mode not in ('L', 'RGB'):
            image = image.convert('RGB')
        image = fit(image, 120)
        image.save(self.object.img.path)
        self.object.avatar_complete = True
        self.object.save()
        return super(AvatarCrop, self).form_valid(form)


class VideoAdd(AjaxFormMixin, FormView):
    model = Video
    form_class = VideoAddForm
    template_name = "video/add.html"
    #    success_url = "/_video"

    def form_valid(self, form):
        link = form.cleaned_data.get('video_url')
        if not link[:7] == 'http://':
            link = 'http://%s' % link
        if link.find('youtu.be') != -1:
            link = link.replace('youtu.be/', 'www.youtube.com/watch?v=')
        consumer = oembed.OEmbedConsumer()
        # TODO: more code security here - big chance to get fatal error
        endpoint = get_oembed_end_point(link)
        #
        consumer.addEndpoint(endpoint)
        response = consumer.embed(link)
        result = response.getData()
        obj = Video()
        obj.embedcode = result['html']
        obj.thumbnail = image_from_url(result['thumbnail_url'])
        if result.has_key('duration'):
            obj.duration = result['duration']
        obj.user = self.request.user
        obj.project_name = form.cleaned_data.get('project_name')
        obj.project_url = form.cleaned_data.get('project_url')
        obj.video_provider = get_video_provider_from_link(form.cleaned_data.get('video_url'))
        obj.publish = True
        obj.description = form.cleaned_data.get('description')
        obj.video_url = link
        obj.save()
        obj.slug = gen_shortcut(obj.id)
        tags = form.cleaned_data.get('tags')
        alltags = Tag.objects.all().filter(name__in=tags)
        for tag in tags:
            obj.tags.add(alltags.get(name=tag))
            obj.save()
        self.success_url = obj.get_absolute_url()
        action.send(self.request.user, verb=_('added the video'), action_type=ACTION_ADDED, target=obj,
                    request=self.request)
        return super(VideoAdd, self).form_valid(form)


class VideoDetail(SingleObjectMixin, ListView):
    # For case-sensitive need UTF8_BIN collation in Slug_Field
    paginate_by = 20
    template_name = "video/detail.html"

    def get_object(self, queryset=None):
        return get_object_or_404(Video, slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        kwargs['object'] = self.object
        context = super(VideoDetail, self).get_context_data(**kwargs)
        context['object'].embedcode = update_video_size(context['object'].embedcode, 640, 363)
        context['ctype'] = ContentType.objects.get_for_model(Video)
        self.object.viewcount += 1
        if self.request.user.is_authenticated():
            if self.request.user not in self.object.users_viewed.all():
                self.object.users_viewed.add(self.request.user)
        self.object.save()
        return context

    def get_queryset(self):
        self.object = self.get_object()
        return Nnmcomment.public.get_tree(self.object)


class VideoTimelineFeed(ListView):
    paginate_by = 5
    model = Video
    template_name = "video/timeline.html"

    def get_queryset(self):
        ctype = ContentType.objects.get_for_model(Tag)
        tags_id = Follow.objects.filter(user=self.request.user, content_type=ctype).values_list('object_id', flat=True)
        tags = Tag.objects.filter(pk__in=tags_id)
        return Video.objects.filter(tags__in=tags).order_by('-created_date').distinct()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(VideoTimelineFeed, self).get_context_data(**kwargs)
        context['tab'] = 'timeline'
        context['tab_message'] = 'TODAY:'
        return context


class VideoPopularFeed(ListView):
    paginate_by = 12
    model = Video
    template_name = "video/feed.html"

    def get_queryset(self):
        return Video.objects.filter(created_date__gte=datetime.now() - timedelta(days=1)).order_by('-viewcount')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(VideoPopularFeed, self).get_context_data(**kwargs)
        context['tab'] = 'popular'
        context['tab_message'] = 'POPULAR AT 24 HOURS AND MAX VIEWS:'
        return context


class VideoLatestFeed(ListView):
    model = Video
    paginate_by = 12
    template_name = "video/feed.html"

    def get_queryset(self):
        return Video.objects.order_by('-created_date')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(VideoLatestFeed, self).get_context_data(**kwargs)
        context['tab'] = 'latest'
        context['tab_message'] = 'ALL LATEST VIDEOS:'
        return context


class VideoLovedFeed(ListView):
    paginate_by = 12
    model = Video
    template_name = "video/feed.html"

    def get_queryset(self):
        return Video.objects.filter(created_date__gte=datetime.now() - timedelta(days=1)).order_by('-viewcount')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(VideoLovedFeed, self).get_context_data(**kwargs)
        context['tab'] = 'loved'
        context['tab_message'] = 'LOVED ON 24 HOURS:'
        return context


class TagSubscribers(TagDetail):
    template_name = "tag/subscribers.html"

    def get_context_data(self, **kwargs):
        context = super(TagSubscribers, self).get_context_data(**kwargs)
        context['tab'] = 'subscribers'
        return context


class UserActivity(UserPathMixin, SingleObjectMixin, ListView):
    paginate_by = 20
    template_name = "user/activity.html"

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(UserActivity, self).get_context_data(**kwargs)
        #        ctype = ContentType.objects.get_for_model(User)
        context['actions_list'] = Action.objects.filter(user=self.object)
        context['tab'] = 'activity'
        context['tab_message'] = 'THIS USER ACTIVITY:'
        return context

    def get_queryset(self):
        self.object = self.get_object()
        return Action.objects.filter(user=self.object)  # filter(action_type__gt=1)


class UserVideoAdded(UserPathMixin, SingleObjectMixin, ListView):
    paginate_by = 12
    template_name = "user/added_video.html"

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(UserVideoAdded, self).get_context_data(**kwargs)
        context['added'] = Video.objects.filter(user=self.object).count()
        context['ctype'] = ContentType.objects.get_for_model(get_user_model())
        context['tab'] = 'added'
        context['tab_message'] = 'VIDEO ADDED THIS USER:'
        return context

    def get_queryset(self):
        self.object = self.get_object()
        return Video.objects.filter(user=self.object).order_by('-created_date')


class UserVideoLoved(UserPathMixin, SingleObjectMixin, ListView):
    paginate_by = 12
    template_name = "user/loved_video.html"

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(UserVideoLoved, self).get_context_data(**kwargs)
        context['added'] = Video.objects.filter(user=self.object).count()
        context['ctype'] = ContentType.objects.get_for_model(get_user_model())
        context['tab'] = 'loved'
        context['tab_message'] = 'LOVED VIDEOS:'
        return context

    def get_queryset(self):
        self.object = self.get_object()
        follow = self.object.follow_set.filter(content_type=ContentType.objects.get_for_model(Video)).values_list(
            'object_id', flat=True)
        return Video.objects.filter(id__in=follow)


class UserFollowTags(UserPathMixin, SingleObjectMixin, ListView):
    paginate_by = 20
    template_name = "user/follow_tags.html"

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(UserFollowTags, self).get_context_data(**kwargs)
        context['added'] = Video.objects.filter(user=self.object).count()
        context['ctype'] = ContentType.objects.get_for_model(get_user_model())
        context['tab'] = 'follow_tags'
        context['tab_message'] = 'USER FOLLOW THIS TAGS:'
        return context

    def get_queryset(self):
        self.object = self.get_object()
        follow = self.object.follow_set.filter(content_type=ContentType.objects.get_for_model(Tag)).values_list(
            'object_id', flat=True)
        return Tag.objects.filter(id__in=follow)


class UserFollowUsers(UserPathMixin, SingleObjectMixin, ListView):
    paginate_by = 20
    template_name = "user/user_follow_list.html"

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(UserFollowUsers, self).get_context_data(**kwargs)
        context['added'] = Video.objects.filter(user=self.object).count()
        context['ctype'] = ContentType.objects.get_for_model(get_user_model())
        context['tab'] = 'follow_users'
        context['tab_message'] = 'USER FOLLOW THIS USERS:'
        return context

    def get_queryset(self):
        self.object = self.get_object()
        follow = self.object.follow_set.filter(
            content_type=ContentType.objects.get_for_model(get_user_model())).values_list('object_id', flat=True)
        return get_user_model().objects.filter(id__in=follow)


class UserFollowerUsers(UserPathMixin, SingleObjectMixin, ListView):
    paginate_by = 20
    template_name = "user/user_follow_list.html"

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(UserFollowerUsers, self).get_context_data(**kwargs)
        context['added'] = Video.objects.filter(user=self.object).count()
        context['ctype'] = ContentType.objects.get_for_model(get_user_model())
        context['tab'] = 'follower_users'
        context['tab_message'] = 'USERS FOLLOW ON THIS USER:'
        return context

    def get_queryset(self):
        self.object = self.get_object()
        followers = Follow.objects.filter(object_id=self.object.id,
                                          content_type=ContentType.objects.get_for_model(get_user_model())).\
            values_list('user', flat=True)
        return get_user_model().objects.filter(id__in=followers)


def redirect_page_not_found(request):
    response = render_to_response('errors/404.html', {}, context_instance=RequestContext(request))
    response.status_code = 404
    return response


def redirect_500_error(request):
    return render_to_response('errors/500.html', {}, context_instance=RequestContext(request))


class AttachedCommentMixin(object):
    paginate_by = 40

    def get_queryset(self):
        self.object = self.get_object()
        return Nnmcomment.public.get_tree(self.object)
