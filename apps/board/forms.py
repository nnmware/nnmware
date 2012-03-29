import re
from django import forms
from django.forms.models import ModelForm

from nnmware.apps.board.models import Board, Category


class BoardForm(ModelForm):
    category = \
    forms.ModelChoiceField(queryset=Category.objects.filter(rootnode=False))

    class Meta:
        model = Board
        fields = ('category', 'title', 'description')
