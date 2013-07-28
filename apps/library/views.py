from django.contrib import messages
from django.db.models import Q
from django.views.generic import ListView, DateDetailView, YearArchiveView,\
    MonthArchiveView, DayArchiveView, CreateView
from django.utils.translation import ugettext_lazy as _
from nnmware.core.data import get_queryset_category

from nnmware.apps.library.forms import *
from nnmware.core.views import *
from nnmware.core.abstract import STATUS_MODERATION, STATUS_LOCKED, STATUS_DELETE
from nnmware.apps.library.models import Publication


class PublicationDetail(AttachedFilesMixin, DateDetailView):
    model = Publication
    date_field = 'created_date'


class PublicationList(ListView):
    model = Publication

    def get_queryset(self):
        result = Publication.objects.exclude(
            Q(status=STATUS_DELETE) |
            Q(status=STATUS_MODERATION) |
            Q(status=STATUS_LOCKED)
            ).order_by('-created_date')
        messages.add_message(self.request, messages.INFO,
            _('Found %(len)s articles') % {'len': len(result)})
        return result


class PublicationDateTemplate(object):
    template_name = 'article/article_list.html'
    model = Publication
    date_field = 'created_date'
    context_object_name = "object_list"
    make_object_list = True
    allow_empty = True


class PublicationYearList(PublicationDateTemplate, YearArchiveView):
    pass


class PublicationMonthList(PublicationDateTemplate, MonthArchiveView):
    pass


class PublicationDayList(PublicationDateTemplate, DayArchiveView):
    pass


class PublicationMyList(CurrentUserAuthenticated, ListView):
    model = Publication

    def get_queryset(self):
        result = Publication.objects.exclude(status=STATUS_LOCKED)
        result = result.filter(user=self.request.user)
        messages.add_message(self.request, messages.INFO,
            _('You have %(len)s active articles') % {'len': len(result)})
        return result


class PublicationLockedList(CurrentUserAuthenticated, ListView):
    model = Publication

    def get_queryset(self):
        result = Publication.objects.filter(status=STATUS_LOCKED)
        messages.add_message(self.request, messages.INFO, _('You have %(len)s locked articles') % {'len': len(result)})
        return result


class PublicationUpdatedList(ListView):
    model = Publication

    def get_queryset(self):
        result = Publication.objects.order_by('-updated_date')
        messages.add_message(self.request, messages.INFO, _('Found %(len)s articles') % {'len': len(result)})
        return result


class PublicationPopularList(ListView):
    model = Publication

    def get_queryset(self):
        result = Publication.objects.order_by('-comments')
        messages.add_message(self.request, messages.INFO, _('Found %(len)s articles') % {'len': len(result)})
        return result


class PublicationModerationList(CurrentUserEditor, ListView):
    model = Publication

    def get_queryset(self):
        result = Publication.objects.filter(status=STATUS_MODERATION)
        messages.add_message(self.request, messages.INFO, _('Found %(len)s articles on moderation') % {'len': len(result)})
        return result


class PublicationDeletedList(CurrentUserSuperuser, ListView):
    model = Publication

    def get_queryset(self):
        result = Publication.objects.filter(status=STATUS_DELETE)
        messages.add_message(self.request, messages.INFO, _('Found %(len)s deleted articles') % {'len': len(result)})
        return result


class PublicationAuthor(ListView):
    template_name = 'article/article_list.html'
    model = Publication

    def get_queryset(self):
        author = get_object_or_404(get_user_model(), username__iexact=self.kwargs['username'])
        result = Publication.objects.filter(user=author)
        messages.add_message(self.request, messages.INFO, _('For this author found- %(len)s results ') % {'len': len(result)})
        return result


class PublicationCategory(ListView):
    template_name = 'article/article_list.html'
    model = Publication

    def get_queryset(self):
        result = get_queryset_category(self, Publication, PublicationCategory)
        messages.add_message(self.request, messages.INFO, _('It this category found- %(len)s results ') % {'len': len(result)})
        return result


class PublicationSearch(ListView):
    model = Publication

    def get_queryset(self):
        query = self.request.GET.get('q')
        result = Publication.objects.filter(content__icontains=query)
        messages.add_message(self.request, messages.INFO, _('On search in articles found- %(len)s results ') % {'len': len(result)})
        return result


class PublicationEdit(CurrentUserAuthor, UpdateView):
    """
    Check the Publication.user = request.user
    """
    model = Publication
    form_class = PublicationEditForm
    template_name = "article/form_edit.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PublicationEdit, self).get_context_data(**kwargs)
        context['action'] = reverse("article_edit",  args=[self.object.id])
        return context


class PublicationEditEditor(CurrentUserEditor, UpdateView):
    model = Publication
    form_class = PublicationEditForm
    template_name = "article/form_edit.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PublicationEditEditor, self).get_context_data(**kwargs)
        context['action'] = reverse("article_edit_editor",
            args=[self.object.id])
        return context


class PublicationEditAdmin(CurrentUserSuperuser, UpdateView):
    model = Publication
    form_class = PublicationEditForm
    template_name = "article/form_edit.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PublicationEditAdmin, self).get_context_data(**kwargs)
        context['action'] = reverse("article_edit_admin",
            args=[self.object.id])
        return context


class PublicationStatus(CurrentUserAuthor, UpdateView):
    model = Publication
    form_class = PublicationStatusForm
    template_name = "article/form_status.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PublicationStatus, self).get_context_data(**kwargs)
        context['action'] = reverse("article_status",  args=[self.object.id])
        return context


class PublicationStatusEditor(CurrentUserEditor, UpdateView):
    model = Publication
    form_class = PublicationStatusEditorForm
    template_name = "article/form_status_editor.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PublicationStatusEditor, self).get_context_data(**kwargs)
        context['action'] = reverse("article_status_editor", args=[self.object.id])
        return context


class PublicationStatusAdmin(CurrentUserSuperuser, UpdateView):
    model = Publication
    form_class = PublicationStatusAdminForm
    template_name = "article/form_status_admin.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PublicationStatusAdmin, self).get_context_data(**kwargs)
        context['action'] = reverse("article_status_admin", args=[self.object.id])
        return context


class PublicationAdd(AjaxFormMixin, CreateView):
    model = Publication
    form_class = PublicationAddForm
    template_name = "article/form.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.status = STATUS_MODERATION
        return super(PublicationAdd, self).form_valid(form)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PublicationAdd, self).get_context_data(**kwargs)
        context['action'] = reverse("article_add")
        return context
