from django.contrib import messages
from django.db.models import Q
from django.views.generic import ListView, DateDetailView, YearArchiveView,\
    MonthArchiveView, DayArchiveView, CreateView
from django.utils.translation import ugettext_lazy as _
from nnmware.core.data import get_queryset_category

from nnmware.apps.article.forms import *
from nnmware.core.views import *
from nnmware.core.abstract import STATUS_MODERATION, STATUS_LOCKED, STATUS_DELETE


class ArticleDetail(AttachedFilesMixin, DateDetailView):
    model = Article
    date_field = 'created_date'


class ArticleList(ListView):
    model = Article

    def get_queryset(self):
        result = Article.objects.exclude(
            Q(status=STATUS_DELETE) |
            Q(status=STATUS_MODERATION) |
            Q(status=STATUS_LOCKED)
            ).order_by('-created_date')
        messages.add_message(self.request, messages.INFO,
            _('Found %(len)s articles') % {'len': len(result)})
        return result


class ArticleDateTemplate(object):
    template_name = 'article/article_list.html'
    model = Article
    date_field = 'created_date'
    context_object_name = "object_list"
    make_object_list = True
    allow_empty = True


class ArticleYearList(ArticleDateTemplate, YearArchiveView):
    pass


class ArticleMonthList(ArticleDateTemplate, MonthArchiveView):
    pass


class ArticleDayList(ArticleDateTemplate, DayArchiveView):
    pass


class ArticleMyList(CurrentUserAuthenticated, ListView):
    model = Article

    def get_queryset(self):
        result = Article.objects.exclude(status=STATUS_LOCKED)
        result = result.filter(user=self.request.user)
        messages.add_message(self.request, messages.INFO,
            _('You have %(len)s active articles') % {'len': len(result)})
        return result


class ArticleLockedList(CurrentUserAuthenticated, ListView):
    model = Article

    def get_queryset(self):
        result = Article.objects.filter(status=STATUS_LOCKED)
        messages.add_message(self.request, messages.INFO, _('You have %(len)s locked articles') % {'len': len(result)})
        return result


class ArticleUpdatedList(ListView):
    model = Article

    def get_queryset(self):
        result = Article.objects.order_by('-updated_date')
        messages.add_message(self.request, messages.INFO, _('Found %(len)s articles') % {'len': len(result)})
        return result


class ArticlePopularList(ListView):
    model = Article

    def get_queryset(self):
        result = Article.objects.order_by('-comments')
        messages.add_message(self.request, messages.INFO, _('Found %(len)s articles') % {'len': len(result)})
        return result


class ArticleModerationList(CurrentUserEditor, ListView):
    model = Article

    def get_queryset(self):
        result = Article.objects.filter(status=STATUS_MODERATION)
        messages.add_message(self.request, messages.INFO, _('Found %(len)s articles on moderation') % {'len': len(result)})
        return result


class ArticleDeletedList(CurrentUserSuperuser, ListView):
    model = Article

    def get_queryset(self):
        result = Article.objects.filter(status=STATUS_DELETE)
        messages.add_message(self.request, messages.INFO, _('Found %(len)s deleted articles') % {'len': len(result)})
        return result


class ArticleAuthor(ListView):
    template_name = 'article/article_list.html'
    model = Article

    def get_queryset(self):
        author = get_object_or_404(get_user_model(), username__iexact=self.kwargs['username'])
        result = Article.objects.filter(user=author)
        messages.add_message(self.request, messages.INFO, _('For this author found- %(len)s results ') % {'len': len(result)})
        return result


class ArticleCategory(ListView):
    template_name = 'article/article_list.html'
    model = Article

    def get_queryset(self):
        result = get_queryset_category(self, Article, Category)
        messages.add_message(self.request, messages.INFO, _('It this category found- %(len)s results ') % {'len': len(result)})
        return result


class ArticleSearch(ListView):
    model = Article

    def get_queryset(self):
        query = self.request.GET.get('q')
        result = Article.objects.filter(content__icontains=query)
        messages.add_message(self.request, messages.INFO, _('On search in articles found- %(len)s results ') % {'len': len(result)})
        return result


class ArticleEdit(CurrentUserAuthor, UpdateView):
    """
    Check the Article.user = request.user
    """
    model = Article
    form_class = ArticleEditForm
    template_name = "article/form_edit.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ArticleEdit, self).get_context_data(**kwargs)
        context['action'] = reverse("article_edit",  args=[self.object.id])
        return context


class ArticleEditEditor(CurrentUserEditor, UpdateView):
    model = Article
    form_class = ArticleEditForm
    template_name = "article/form_edit.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ArticleEditEditor, self).get_context_data(**kwargs)
        context['action'] = reverse("article_edit_editor",
            args=[self.object.id])
        return context


class ArticleEditAdmin(CurrentUserSuperuser, UpdateView):
    model = Article
    form_class = ArticleEditForm
    template_name = "article/form_edit.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ArticleEditAdmin, self).get_context_data(**kwargs)
        context['action'] = reverse("article_edit_admin",
            args=[self.object.id])
        return context


class ArticleStatus(CurrentUserAuthor, UpdateView):
    model = Article
    form_class = ArticleStatusForm
    template_name = "article/form_status.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ArticleStatus, self).get_context_data(**kwargs)
        context['action'] = reverse("article_status",  args=[self.object.id])
        return context


class ArticleStatusEditor(CurrentUserEditor, UpdateView):
    model = Article
    form_class = ArticleStatusEditorForm
    template_name = "article/form_status_editor.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ArticleStatusEditor, self).get_context_data(**kwargs)
        context['action'] = reverse("article_status_editor", args=[self.object.id])
        return context


class ArticleStatusAdmin(CurrentUserSuperuser, UpdateView):
    model = Article
    form_class = ArticleStatusAdminForm
    template_name = "article/form_status_admin.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ArticleStatusAdmin, self).get_context_data(**kwargs)
        context['action'] = reverse("article_status_admin", args=[self.object.id])
        return context


class ArticleAdd(AjaxFormMixin, CreateView):
    model = Article
    form_class = ArticleAddForm
    template_name = "article/form.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.status = STATUS_MODERATION
        return super(ArticleAdd, self).form_valid(form)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ArticleAdd, self).get_context_data(**kwargs)
        context['action'] = reverse("article_add")
        return context
