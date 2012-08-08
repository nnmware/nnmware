from django.contrib import admin
from django.contrib.contenttypes import generic
from nnmware.core.admin import TreeAdmin, UnitAdmin
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.shop.models import *
from nnmware.core.admin import ColorAdmin

class ProductParameterValueInline(generic.GenericStackedInline):
    model = ProductParameterValue
    extra = 0
    fields = (('parameter','value'),)


class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('created_date','updated_date')
    list_display = ("name", "category", "created_date",'quantity','amount')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ ProductParameterValueInline, ]
    fieldsets = (
        (_("Product"), {"fields": [('name','category'),
            ('slug','order_in_list'),
            ('amount','quantity'),
            ('description',),
            ('color',"created_date",'updated_date'),
            ('shop_pn','vendor_pn'),
        ]}),
        )


class ProductCategoryAdmin(TreeAdmin):
    list_display = ("name", "_parents_repr")

class ProductParameterAdmin(admin.ModelAdmin):

    list_display = ("name", "unit")


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(ParameterUnit, UnitAdmin)
admin.site.register(ProductParameter, ProductParameterAdmin)
admin.site.register(ProductColor, ColorAdmin)
