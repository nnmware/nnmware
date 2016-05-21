# nnmware(c)2012-2016

from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from nnmware.apps.publication.models import Publication, PublicationCategory
from nnmware.core.admin import TreeAdmin


@admin.register(PublicationCategory)
class PublicationCategoryAdmin(TreeAdmin):
    fieldsets = (
        (_("Main"), {"fields": [("name", "slug"), ("parent", "login_required",)]}),
        (_("Description"), {"classes": ("collapse",),
                            "fields": [("description",), ("position", "rootnode"), ('admins', )]}),
    )


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('Publication'), {'fields': [('user', 'enabled', 'category', 'region')]}),
        (_('Content'), {'fields': [('name',), ('description',)]}),
        (_('Meta'), {'fields': [('created_date', 'updated_date')]}),
    )
    list_display = ('user', 'created_date', 'name', 'status')
    list_filter = ('created_date',)
    date_hierarchy = 'created_date'
    search_fields = ('name', 'user__username')
    readonly_fields = ('created_date', 'updated_date')
