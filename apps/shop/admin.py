from django.contrib import admin
from django.contrib.contenttypes import generic
from nnmware.core.admin import TreeAdmin, UnitAdmin

from nnmware.apps.shop.models import Product, ProductCategory, ParameterUnit, ProductParameterValue, ProductParameter

class ProductParameterValueInline(generic.GenericStackedInline):
    model = ProductParameterValue
    extra = 0
    fields = (('parameter','string_value'),)


class ProductAdmin(admin.ModelAdmin):

    list_display = ("name", "category", "created_date")
    inlines = [ ProductParameterValueInline, ]


class ProductCategoryAdmin(TreeAdmin):
    list_display = ("name", "_parents_repr")

class ProductParameterAdmin(admin.ModelAdmin):

    list_display = ("name", "unit", "is_string")


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(ParameterUnit, UnitAdmin)
admin.site.register(ProductParameter, ProductParameterAdmin)
