# -*- coding: utf-8 -*-
from datetime import datetime
import Image
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import permission_required, login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models.aggregates import Sum
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, render_to_response, get_object_or_404
from django.template.base import Template
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateResponseMixin, TemplateView, View
from django.views.generic.dates import YearArchiveView, MonthArchiveView, DayArchiveView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, BaseFormView, FormMixin, DeleteView, FormView
from django.views.generic.list import ListView
from django.utils.translation import ugettext_lazy as _
from nnmware.core.forms import PassChangeForm, LoginForm, EmailQuickRegisterForm
from nnmware.core.decorators import ssl_required, ssl_not_required
from nnmware.core.ajax import as_json, AjaxLazyAnswer
from nnmware.core.http import redirect
from nnmware.core.imgutil import remove_thumbnails
from nnmware.core.models import JComment, Doc, Pic, Follow, Notice, Message, Action
from nnmware.core.forms import *
from nnmware.core.abstract import STATUS_DELETE


class UserPathMixin(object):

    def get_object(self, queryset=None):
        return get_object_or_404(settings.AUTH_USER_MODEL, username=self.kwargs['username'])


def _adjust_max_comment_length(form):
    """
    Sets the maximum comment length to that default specified in the settings.
    """
    form.base_fields['comment'].max_length = DEFAULT_MAX_JCOMMENT_LENGTH


#@render_to('jcomments/preview.html')
def _preview(request):
    """
    Returns a preview of the comment so that the user may decide if he or she wants to
    edit it before submitting it permanently.
    """
    _adjust_max_comment_length(JCommentForm)
    form = JCommentForm(request.POST or None)
    context = {'next': redirect(request), 'form': form}
    if form.is_valid():
        new_comment = form.save(commit=False)
        context['comment'] = new_comment
    else:
        context['comment'] = None
    return context


class AjaxFormMixin(object):

    def form_valid(self, form):
        if self.request.is_ajax():
            self.success = True
            payload = {'success': self.success, 'location': self.success_url or self.get_success_url()}
            try:
                payload['status_msg'] = self.status_msg
            except :
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
            return super(AjaxFormMixin, self).form_invalid(
                form, *args, **kwargs
            )


class JCommentAdd(AjaxFormMixin, CreateView):
    """
   Form for add a comment. Its Ajax posted and reply href.location after comment create
    """
    form_class = JCommentForm
#    template_name = "jcomments/form.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.content_type = get_object_or_404(ContentType, id=int(self.kwargs['content_type']))
        self.object.object_id = int(self.kwargs['object_id'])
        try:
            self.object.parent_id = int(self.kwargs['parent_id'])
        except:
            pass
        self.object.save()
        self.success_url = self.object.content_object.get_absolute_url()
        return super(JCommentAdd, self).form_valid(form)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(JCommentAdd, self).get_context_data(**kwargs)
        try:
            context['action'] = reverse("jcomment_parent_add", kwargs={'content_type': self.kwargs['content_type'],
                                                                       'object_id': self.kwargs['object_id'],
                                                                       'parent_id': self.kwargs['parent_id']})
        except:
            context['action'] = reverse("jcomment_add",
                kwargs={'content_type': self.kwargs['content_type'], 'object_id': self.kwargs['object_id']})
        return context


class JCommentEditBase(UpdateView):
    model = JComment

    def get_success_url(self):
        return self.object.content_object.get_absolute_url()


class JCommentEdit(JCommentEditBase):
    form_class = JCommentForm
    template_name = "jcomments/form.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(JCommentEdit, self).get_context_data(**kwargs)
        context['action'] = reverse("jcomment_edit", args=[self.object.id])
        return context


class JCommentStatus(JCommentEditBase):
    form_class = JCommentStatusForm
    template_name = "jcomments/form.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(JCommentStatus, self).get_context_data(**kwargs)
        context['action'] = reverse("jcomment_status", args=[self.object.id])
        return context


class JCommentAdminEdit(JCommentEditBase):
    form_class = JCommentAdminForm
    template_name = "jcomments/form.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(JCommentAdminEdit, self).get_context_data(**kwargs)
        context['action'] = reverse("jcomment_edit_admin", args=[self.object.id])
        return context


class JCommentAdminStatus(JCommentEditBase):
    form_class = JCommentAdminStatusForm
    template_name = "jcomments/form.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(JCommentAdminStatus, self).get_context_data(**kwargs)
        context['action'] = reverse("jcomment_status_admin", args=[self.object.id])
        return context


class JCommentEditorEdit(JCommentEditBase):
    form_class = JCommentEditorForm
    template_name = "jcomments/form.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(JCommentEditorEdit, self).get_context_data(**kwargs)
        context['action'] = reverse("jcomment_edit_editor", args=[self.object.id])
        return context


class JCommentEditorStatus(JCommentEditBase):
    form_class = JCommentEditorStatusForm
    template_name = "jcomments/form.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(JCommentEditorStatus, self).get_context_data(**kwargs)
        context['action'] = reverse("jcomment_status_editor", args=[self.object.id])
        return context


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
    #form_class = JDocDeleteForm
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
        if not self.request.user.has_perm('%s.change_%s' % (self.model._meta.app_label, self.model._meta.module_name)):
            raise Http404
        return super(CurrentUserEditor, self).dispatch(*args, **kwargs)


class CurrentUserCreator(object):
    """ Generic create view that checks permissions """

    def dispatch(self, *args, **kwargs):
        if not self.request.user.has_perm('%s.create_%s' % (self.model._meta.app_label, self.model._meta.module_name)):
            raise Http404
        return super(CurrentUserCreator, self).dispatch(*args, **kwargs)


class AttachedImagesMixin(object):
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(AttachedImagesMixin, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the images
        pics = Pic.objects.metalinks_for_object(self.object)
        pics_size = pics.aggregate(Sum('size'))['size__sum']
        context['pics'] = pics
        context['pics_size'] = pics_size
        return context

class AttachedFilesMixin(object):
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(AttachedFilesMixin, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the docs and files
        docs = Doc.objects.metalinks_for_object(self.object)
        docs_size = docs.aggregate(Sum('size'))['size__sum']
        context['docs'] = docs
        context['docs_size'] = docs_size
        return context

class AttachedMixin(AttachedFilesMixin,AttachedImagesMixin):
    pass

class TagDetail(DetailView):
    model = Tag
    slug_field = 'slug'
    template_name = "tag/detail.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TagDetail,self).get_context_data(**kwargs)
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
        self.request.user.set_password(form.cleaned_data.get('new_password2'))
        self.request.user.save()
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
        u = get_user_model()(username=username,email=email)
        u.set_password(password)
        u.is_active = True
        u.save()
        user = authenticate(username=username, password=password)
        self.user = user
        login(self.request, user)
        return super(EmailQuickRegisterView, self).form_valid(form)
