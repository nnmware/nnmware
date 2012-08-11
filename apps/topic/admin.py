from django.contrib import admin
from nnmware.core.admin import TreeAdmin, MetaDataAdmin

from nnmware.apps.topic.models import Topic, Category
from copy import deepcopy

topic_fieldsets = deepcopy(MetaDataAdmin.fieldsets)
topic_fieldsets[0][1]["fields"].append(("category"), )


class TopicAdmin(MetaDataAdmin):
    """
    Admin class for topics.
    """
    actions = None
    fieldsets = topic_fieldsets
    list_display = ("title", "category", "created_date", "user", "status",
                    "admin_link")


class CategoryAdmin(TreeAdmin):
    list_display = ("title", "_parents_repr", "user", "status", "admin_link")

admin.site.register(Topic, TopicAdmin)
admin.site.register(Category, CategoryAdmin)
