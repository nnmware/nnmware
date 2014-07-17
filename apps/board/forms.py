# -*- coding: utf-8 -*-

from django import forms
from django.forms.models import ModelForm

from nnmware.apps.board.models import Board, BoardCategory


class BoardForm(ModelForm):
    category = forms.ModelChoiceField(queryset=BoardCategory.objects.filter(rootnode=False))

    class Meta:
        model = Board
        fields = ('category', 'title', 'description')
