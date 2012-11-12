# -*- coding: utf-8 -*-
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
    list_display = ("name", "category", 'vendor',"created_date",'quantity','amount','shop_pn','vendor_pn')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ ProductParameterValueInline, ]
    fieldsets = (
        (_("Product"), {"fields": [('name','category'),
            ('slug','vendor','is_deleted'),
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

class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0
    fields = (('product_pn','product_name'),('quantity','amount'),)

class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ('created_date','updated_date')
    list_display = ("user", "created_date", 'status',"fullamount",'address','last_name','first_name')
    inlines = [ OrderItemInline, ]
    fieldsets = (
        (_("Order"), {"fields": [('user','status'),
            ("last_name",'first_name','middle_name'),
            ("created_date",'updated_date'),
            ('address'),
            ('comment'),
        ]}),
        )
    ordering = ('-created_date','user','address')


class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ("user", "zipcode", 'city',"street",'house_number','last_name','first_name')
    fieldsets = (
        (_("Delivery Address"), {"fields": [('user',),
            ("last_name",'first_name','middle_name'),
            ('country','region'),
            ("zipcode",'city','street'),
            ('house_number','building','flat_number'),
            ('phone','skype'),
        ]}),
        )

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("name", "email", 'created_date',"ip",'user_agent')
    fieldsets = (
        (_("Feedback"), {"fields": [('name','email'), ('message',),
            ('created_date','ip','user_agent'),]}),
        )
    ordering = ('-created_date','name','email')
    readonly_fields = ('ip','user_agent','created_date')

class ShopNewsAdmin(admin.ModelAdmin):
    list_display = ("title", 'created_date')
    fieldsets = (
        (_("Shop News"), {"fields": [('title',),('created_date','enabled'), ('teaser',),
                                    ('content'),]}),
        )
    ordering = ('-created_date','title')

class ShopArticleAdmin(admin.ModelAdmin):
    list_display = ("title", 'created_date')
    fieldsets = (
        (_("Shop Articles"), {"fields": [('title',),('created_date','enabled'), ('teaser',),
                                     ('content'),]}),
        )
    ordering = ('-created_date','title')


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(ParameterUnit, UnitAdmin)
admin.site.register(ProductParameter, ProductParameterAdmin)
admin.site.register(ProductColor, ColorAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(CargoService, VendorAdmin)
admin.site.register(Basket, BasketAdmin)
admin.site.register(ProductParameterCategory, ProductParameterCategoryAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(DeliveryAddress, DeliveryAddressAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(ShopNews, ShopNewsAdmin)
admin.site.register(ShopArticle, ShopArticleAdmin)
