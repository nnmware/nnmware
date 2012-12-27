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
    list_display = ("name", "category", 'vendor',"created_date",'quantity','amount','shop_pn','vendor_pn','visible')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ ProductParameterValueInline, ]
    fieldsets = (
        (_("Product"), {"fields": [('name','category'),
            ('slug','vendor','visible','avail'),
            ('amount','quantity'),
            ('description',),
            ('color',"created_date",'updated_date'),
            ('shop_pn','vendor_pn'),
            ('order_in_list','enabled'),
            ('teaser'),('discount','discount_percent','special_offer'),
        ]}),
        )


class ProductCategoryAdmin(TreeAdmin):
    pass

    class Media:
        js = ['/static/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
              '/static/grappelli/tinymce_setup/tinymce_setup.js',]
    #list_display = ("name", "_parents_repr")

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
    fields = (('product_pn','product_name'),('quantity','amount'),('product_url','product_origin'))

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
        (_("Feedback"), {"fields": [('name','email'), ('message',),('answer',),
            ('created_date','ip','user_agent'),]}),
        )
    ordering = ('-created_date','name','email')
    readonly_fields = ('ip','user_agent','created_date')

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name','slide_thumbnail','created_date','visible','vip',"ip",'user_agent',"user")
    fieldsets = (
        (_("Review"), {"fields": [('name','position','visible'),('vip','img'), ('message',),
                                    ('created_date','ip','user_agent'),('user',)]}),
        )
    ordering = ('-created_date','user','visible')
    readonly_fields = ('ip','user_agent','created_date')

class SpecialOfferAdmin(admin.ModelAdmin):
    class Media:
        js = ['/static/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
              '/static/grappelli/tinymce_setup/tinymce_setup.js',]
    list_display = ("title", 'start_date','end_date','slide_thumbnail','enabled')
    fieldsets = (
        (_("SpecialOffer"), {"fields": [('title',), ('start_date','end_date'),
                                  ('enabled','slug','order_in_list'),('img',),('text',)]}),
        )
    ordering = ('-start_date','-end_date')


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
admin.site.register(Review, ReviewAdmin)
admin.site.register(SpecialOffer, SpecialOfferAdmin)
