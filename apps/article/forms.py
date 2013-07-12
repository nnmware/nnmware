from django import forms
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.article.models import Article
from django.conf import settings
from nnmware.core.models import Tag
from nnmware.core.utils import tags_normalize
from nnmware.core.forms import TagsMixinForm


class ArticleEditForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title', 'category', 'slug', 'content', 'description')


class ArticleAddForm(TagsMixinForm):

    class Meta:
        model = Article
        fields = ('title', 'category', 'tags', 'slug', 'content', 'description', 'allow_comments', 'created_date')


class ArticleStatusForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('status', 'created_date', 'allow_comments', 'login_required')


class ArticleStatusEditorForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('status', 'created_date', 'allow_comments', 'allow_docs', 'allow_pics', 'login_required')


class ArticleStatusAdminForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('user', 'status', 'created_date', 'allow_comments', 'allow_docs', 'allow_pics', 'login_required')
