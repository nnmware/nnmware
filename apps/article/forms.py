from django import forms
from nnmware.apps.article.models import Article
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
