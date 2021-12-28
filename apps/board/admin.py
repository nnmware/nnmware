# nnmware(c)2012-2020

from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import gettext as _

from nnmware.apps.board.models import Board, BoardCategory
from nnmware.core.admin import TreeAdmin


@admin.register(BoardCategory)
class BoardCategoryAdmin(TreeAdmin):
    fieldsets = (
        (_("Main"), {"fields": [("name", "slug"), ("parent", "login_required",)]}),
        (_("Description"), {"classes": ("collapse",), "fields": [("description",), ("position", "rootnode"),
                                                                 ('admins',)]})
    )


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('Board'), {'fields': [('user', 'enabled', 'category', 'region')]}),
        (_('Content'), {'fields': [('name',), ('description',)]}),
        (_('Meta'), {'fields': [('created_date', 'updated_date')]}),
    )
    list_display = ('user', 'created_date', 'name')
    list_filter = ('created_date',)
    date_hierarchy = 'created_date'
    search_fields = ('name', 'user__username')
    readonly_fields = ('created_date', 'updated_date')
