from django.contrib import admin
from nnmware.apps.topic.models import Topic, TopicCategory
from nnmware.core.admin import TreeAdmin


class TopicCategoryAdmin(TreeAdmin):
    fieldsets = (
        (_("Main"), {"fields": [("name", "slug"), ("parent", "login_required",)]}),
        (_("Description"), {"classes": ("collapse",),
                            "fields": [("description",), ("ordering", "rootnode"), ('admins', )]}),
    )


class TopicAdmin(admin.ModelAdmin):
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

admin.site.register(Topic, TopicAdmin)
admin.site.register(TopicCategory, TopicCategoryAdmin)
