from django.contrib import admin
from nnmware.core.admin import TreeAdmin

from nnmware.apps.shop.models import Product, ProductCategory


class ProductAdmin(admin.ModelAdmin):

    list_display = ("name", "category", "created_date")


class ProductCategoryAdmin(TreeAdmin):
    list_display = ("name", "_parents_repr", "admin_link")

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductCategory, ProductCategoryAdmin)
