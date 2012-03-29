from django.contrib import admin
from nnmware.apps.board.models import Board, Category
from nnmware.core.admin import TreeAdmin, MetaDataAdmin
from nnmware.core.fields import ImageWithThumbnailField
from nnmware.core.widgets import AdminImageWithThumbnailWidget

from copy import deepcopy

board_fieldsets = deepcopy(MetaDataAdmin.fieldsets)
board_fieldsets[0][1]["fields"].append(("category"), )


class BoardAdmin(MetaDataAdmin):
    """
    Admin class for boards.
    """
    actions = None
    fieldsets = board_fieldsets
    list_display = ("title", "category", "publish_date", "user", "status",
                    "admin_link")


class CategoryAdmin(TreeAdmin):
    list_display = ("title", "_parents_repr", "user", "status", "admin_link")

admin.site.register(Board, BoardAdmin)
admin.site.register(Category, CategoryAdmin)
