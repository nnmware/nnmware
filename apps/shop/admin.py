from django.contrib import admin
from django.contrib.contenttypes import generic
from nnmware.core.admin import TreeAdmin, UnitAdmin
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.shop.models import Product, ProductParameter, ProductColor, ProductParameterValue, \
    Vendor, ProductCategory, ParameterUnit, Basket, ProductParameterCategory
from nnmware.core.admin import ColorAdmin
from nnmware.apps.shop.models import OrderItem, Order

class ProductParameterValueInline(generic.GenericStackedInline):
    model = ProductParameterValue
    extra = 0
    fields = (('parameter','value'),)


class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('created_date','updated_date')
    list_display = ("name", "category", 'vendor',"created_date",'quantity','amount','shop_pn','vendor_pn')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ ProductParameterValueInline, ]
    fieldsets = (
        (_("Product"), {"fields": [('name','category'),
            ('slug','vendor'),
            ('amount','quantity'),
            ('description',),
            ('color',"created_date",'updated_date'),
            ('shop_pn','vendor_pn'),
            ('order_in_list'),
            ('teaser'),
        ]}),
        )


class ProductCategoryAdmin(TreeAdmin):
    list_display = ("name", "_parents_repr")

class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ("name",'category' ,"unit")

class ProductParameterCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)

class VendorAdmin(admin.ModelAdmin):
    fieldsets = ((_('Vendor'), {'fields': [('name','country','website'),('description',)]}),)
    list_display = ('name','country','website')

class BasketAdmin(admin.ModelAdmin):
    list_display = ("user", "product",'quantity','created_date','updated_date')

class OrderItemInline(generic.GenericStackedInline):
    model = OrderItem
    extra = 0
    fields = (('product','product_name','quantity','amount'),)

class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ('created_date','updated_date')
    list_display = ("user", "name", 'status',"amount")
    inlines = [ OrderItemInline, ]
    fieldsets = (
        (_("Order"), {"fields": [('user','name'),
            ('status',),
            ('amount','quantity'),
            ("created_date",'updated_date'),
            ('comment'),
        ]}),
        )

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(ParameterUnit, UnitAdmin)
admin.site.register(ProductParameter, ProductParameterAdmin)
admin.site.register(ProductColor, ColorAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(Basket, BasketAdmin)
admin.site.register(ProductParameterCategory, ProductParameterCategoryAdmin)
admin.site.register(Order, OrderAdmin)
