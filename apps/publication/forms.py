from django import forms
from nnmware.apps.publication.models import Publication
from nnmware.core.forms import TagsMixinForm


class PublicationEditForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ('title', 'category', 'slug', 'content', 'description')


class PublicationAddForm(TagsMixinForm):

    class Meta:
        model = Publication
        fields = ('title', 'category', 'tags', 'slug', 'content', 'description', 'allow_comments', 'created_date')


class PublicationStatusForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ('status', 'created_date', 'allow_comments', 'login_required')


class PublicationStatusEditorForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ('status', 'created_date', 'allow_comments', 'allow_docs', 'allow_pics', 'login_required')


class PublicationStatusAdminForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ('user', 'status', 'created_date', 'allow_comments', 'allow_docs', 'allow_pics', 'login_required')
