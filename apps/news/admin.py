# nnmware(c)2012-2020

from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import gettext as _

from nnmware.apps.news.models import News, NewsCategory
from nnmware.core.admin import TreeAdmin


@admin.register(NewsCategory)
class NewsCategoryAdmin(TreeAdmin):
    fieldsets = (
        (_("Main"), {"fields": [("name", "slug"), ("parent", "login_required",)]}),
        (_("Description"), {"classes": ("collapse",),
                            "fields": [("description",), ("position", "rootnode"), ('admins', )]}),
    )


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('Topic'), {'fields': [('user', 'enabled', 'category', 'region')]}),
        (_('Content'), {'fields': [('name',), ('description',)]}),
        (_('Meta'), {'fields': [('created_date', 'updated_date')]}),
    )
    list_display = ('user', 'created_date', 'name')
    list_filter = ('created_date',)
    date_hierarchy = 'created_date'
    search_fields = ('name', 'user__username')
    readonly_fields = ('created_date', 'updated_date')
