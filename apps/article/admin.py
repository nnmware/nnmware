from django.contrib import admin
from nnmware.core.admin import TreeAdmin, MetaDataAdmin

from nnmware.apps.article.models import Article, Category
from copy import deepcopy

articlepost_fieldsets = deepcopy(MetaDataAdmin.fieldsets)
articlepost_fieldsets[0][1]["fields"].append(("category"), )
articlepost_fieldsets[0][1]["fields"].append("content")


class ArticleAdmin(MetaDataAdmin):
    """
     Admin class for blog posts.
     """
    #    actions = None
    fieldsets = articlepost_fieldsets
    list_display = ("title", "category", "publish_date", "user", "status",
                    "admin_link")


class CategoryAdmin(TreeAdmin):
    list_display = ("title", "_parents_repr", "user", "status", "admin_link")

admin.site.register(Article, ArticleAdmin)
admin.site.register(Category, CategoryAdmin)
