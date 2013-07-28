from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.library.models import Publication, PublicationCategory
from nnmware.core.admin import TreeAdmin


class PublicationCategoryAdmin(TreeAdmin):
    fieldsets = (
        (_("Main"), {"fields": [("name", "slug"), ("parent", "login_required",)]}),
        (_("Description"), {"classes": ("collapse",),
                            "fields": [("description",), ("ordering", "rootnode"), ('admins', )]}),
    )


class PublicationAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('Publication'), {'fields': [('user', 'enabled', 'category', 'region')]}),
        (_('Content'), {'fields': [('name',), ('description',)]}),
        (_('Meta'), {'fields': [('created_date', 'updated_date')]}),
    )
    list_display = ('user', 'created_date', 'name')
    list_filter = ('created_date',)
    date_hierarchy = 'created_date'
    search_fields = ('name', 'user__username')
    readonly_fields = ('created_date', 'updated_date')

admin.site.register(Publication, PublicationAdmin)
admin.site.register(PublicationCategory, PublicationCategoryAdmin)
