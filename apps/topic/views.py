# -*- coding: utf-8 -*-

from django.views.generic.dates import DayArchiveView, MonthArchiveView, \
    YearArchiveView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from nnmware.core.constants import STATUS_LOCKED, STATUS_MODERATION, STATUS_DELETE, STATUS_PUBLISHED
from nnmware.apps.topic.forms import TopicAddForm
from nnmware.apps.topic.models import TopicCategory, Topic
from nnmware.apps.topic.forms import TopicForm
from nnmware.core.data import get_queryset_category
from django.contrib import messages
from nnmware.core.views import CurrentUserAuthor, CurrentUserSuperuser, \
    CurrentUserEditor, CurrentUserAuthenticated, AttachedCommentMixin, TabMixinView


class TopicList(ListView):
    model = Topic


class TopicUpdatedList(ListView):
    model = Topic

    def get_queryset(self):
        result = Topic.objects.order_by("-updated_date")
        messages.add_message(self.request, messages.INFO,
            _('Found %(len)s results ') % {'len': len(result)})
        return result


class TopicPopularList(ListView):
    model = Topic

    def get_queryset(self):
        result = Topic.objects.order_by("-comments")
        messages.add_message(self.request, messages.INFO,
            _('Found %(len)s results ') % {'len': len(result)})
        return result


class TopicUserList(ListView):
    model = Topic

    def get_queryset(self):
        result = Topic.objects.filter(user=self.request.user)
        messages.add_message(self.request, messages.INFO,
            _('Found %(len)s results ') % {'len': len(result)})
        return result


class TopicDateTemplate(object):
    template_name = 'topic/topic_list.html'
    model = Topic
    date_field = 'created_date'
    context_object_name = "object_list"
    make_object_list = True
    allow_empty = True


class TopicYearList(TopicDateTemplate, YearArchiveView):
    pass


class TopicMonthList(TopicDateTemplate, MonthArchiveView):
    pass


class TopicDayList(TopicDateTemplate, DayArchiveView):
    pass


class TopicCategoryView(ListView):
    template_name = 'topic/topic_list.html'
    model = Topic

    def get_queryset(self):
        result = get_queryset_category(self, Topic, TopicCategory)
        messages.info(self.request,
            _('In this category found- %(len)s results ') %
            {'len': len(result)})
        return result


class TopicAdd(TabMixinView, CurrentUserAuthenticated, CreateView):
    model = Topic
    form_class = TopicAddForm
    template_name = "topic/add.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.status = STATUS_PUBLISHED
        self.object.ip = self.request.META['REMOTE_ADDR']
        self.object.user_agent = self.request.META['HTTP_USER_AGENT']
        self.object.save()
        return super(TopicAdd, self).form_valid(form)

    def get_success_url(self):
        return reverse('topic_detail', args=[self.object.pk])


class TopicDetail(AttachedCommentMixin, SingleObjectMixin, ListView):
    paginate_by = 20
    model = Topic
    template_name = 'topic/one.html'

    def get_object(self, queryset=None):
        return Topic.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super(TopicDetail, self).get_context_data(**kwargs)
        return context


class TopicEdit(CurrentUserAuthor, UpdateView):
    model = Topic
    form_class = TopicForm
    template_name = "topic/form.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TopicEdit, self).get_context_data(**kwargs)
        context['action'] = reverse("topic_edit", args=[self.object.id])
        return context


class TopicStatus(CurrentUserAuthor, UpdateView):
    model = Topic
    form_class = TopicForm
    template_name = "topic/form.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TopicStatus, self).get_context_data(**kwargs)
        context['action'] = reverse("topic_status", args=[self.object.id])
        return context


class TopicAdminEdit(CurrentUserSuperuser, UpdateView):
    model = Topic
    form_class = TopicForm
    template_name = "topic/form.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TopicAdminEdit, self).get_context_data(**kwargs)
        context['action'] = reverse("topic_edit_admin", args=[self.object.id])
        return context


class TopicAdminStatus(CurrentUserSuperuser, UpdateView):
    model = Topic
    form_class = TopicForm
    template_name = "topic/form.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TopicAdminStatus, self).get_context_data(**kwargs)
        context['action'] = reverse("topic_status_admin",
            args=[self.object.id])
        return context


class TopicEditorEdit(CurrentUserEditor, UpdateView):
    model = Topic
    form_class = TopicForm
    template_name = "topic/form.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TopicEditorEdit, self).get_context_data(**kwargs)
        context['action'] = reverse("topic_edit_editor", args=[self.object.id])
        return context


class TopicEditorStatus(CurrentUserEditor, UpdateView):
    model = Topic
    form_class = TopicForm
    template_name = "topic/form.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TopicEditorStatus, self).get_context_data(**kwargs)
        context['action'] = reverse("topic_status_editor",
            args=[self.object.id])
        return context


class TopicSearch(ListView):
    model = Topic

    def get_queryset(self):
        query = self.request.GET.get('q')
        qset = (Q(title__icontains=query) | Q(description__icontains=query))
        messages.add_message(self.request, messages.INFO, 'Hello world.')
        result = Topic.objects.filter(qset)
        messages.add_message(self.request, messages.INFO,
            _('On search "%(q)s" found- %(len)s ') %
            {'q': query, 'len': len(result)})
        return result


class TopicLockedList(CurrentUserAuthenticated, ListView):
    model = Topic

    def get_queryset(self):
        result = Topic.objects.filter(status=STATUS_LOCKED)
        messages.add_message(self.request, messages.INFO,
            _('You have %(len)s locked topics') % {'len': len(result)})
        return result


class TopicModerationList(CurrentUserEditor, ListView):
    model = Topic

    def get_queryset(self):
        result = Topic.objects.filter(status=STATUS_MODERATION)
        messages.add_message(self.request, messages.INFO,
            _('Found %(len)s topics on moderation') % {'len': len(result)})
        return result


class TopicDeletedList(CurrentUserSuperuser, ListView):
    model = Topic

    def get_queryset(self):
        result = Topic.objects.filter(status=STATUS_DELETE)
        messages.add_message(self.request, messages.INFO,
            _('Found %(len)s deleted topics') % {'len': len(result)})
        return result
