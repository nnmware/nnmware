from django.contrib import admin
from nnmware.apps.board.models import Board, Category
from nnmware.core.admin import TreeAdmin, AbstractDataAdmin

from copy import deepcopy

board_fieldsets = deepcopy(AbstractDataAdmin.fieldsets)
board_fieldsets[0][1]["fields"].append(("category", ), )


class BoardAdmin(AbstractDataAdmin):
    """
    Admin class for boards.
    """
    actions = None
    fieldsets = board_fieldsets
    list_display = ("title", "category", "created_date", "user", "status",
                    "admin_link")


class CategoryAdmin(TreeAdmin):
    list_display = ("title", "_parents_repr", "user", "status", "admin_link")

admin.site.register(Board, BoardAdmin)
admin.site.register(Category, CategoryAdmin)
