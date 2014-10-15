# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from django.utils.translation import ugettext as _

from nnmware.core.admin import TreeAdmin
from nnmware.apps.shop.models import ProductParameterValue, Product, ProductCategory, ProductParameter, \
    ProductParameterCategory, Vendor, Basket, OrderItem, Order, DeliveryAddress, Feedback, ShopCallback, Review, \
    ShopSlider, SpecialOffer, ShopNews, ShopArticle, DeliveryMethod, ServiceCategory, Service


class ProductParameterValueInline(GenericStackedInline):
    model = ProductParameterValue
    extra = 0
    fields = (('parameter', 'value'),)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('created_date', 'updated_date')
    list_display = ("name", "category", 'vendor', "created_date", 'quantity', 'amount', 'shop_pn', 'vendor_pn',
                    'visible')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductParameterValueInline, ]
    fieldsets = (
        (_("Product"), {"fields": [('name', 'category'),
                                   ('slug', 'vendor', 'visible', 'avail'),
                                   ('amount', 'quantity'),
                                   ('description',),
                                   ("created_date", 'updated_date'),
                                   ('shop_pn', 'vendor_pn'),
                                   ('position', 'enabled', 'on_main'),
                                   ('teaser',), ('discount', 'discount_percent', 'special_offer'),
                                   ('colors',), ('materials',), ('related_products',)]}),)


@admin.register(ProductCategory)
class ProductCategoryAdmin(TreeAdmin):
    pass

    class Media:
        js = ('/static/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
              '/static/grappelli/tinymce_setup/tinymce_setup.js')
        # list_display = ("name", "_parents_repr")


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ("name", 'category', "unit")


@admin.register(ProductParameterCategory)
class ProductParameterCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    fieldsets = ((_('Vendor'), {'fields': [('name', 'country', 'website'), ('description',)]}),)
    list_display = ('name', 'country', 'website')


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ("user", "product", 'quantity', 'created_date', 'updated_date')


class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0
    fields = (
        ('product_pn', 'product_name'), ('quantity', 'amount'), ('product_url', 'product_origin'),
        ('is_delivery', 'addon'))


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    change_form_template = 'admin_form/change_form.html'
    readonly_fields = ('created_date', 'updated_date', 'amount_order')
    list_display = (
        "number_order", "user", "created_date", 'status', "amount_order", 'address', 'last_name', 'first_name')
    list_filter = ('user', 'id', 'status')
    inlines = [OrderItemInline, ]
    fieldsets = (
        (_("Order"), {"fields": [('user', 'status', 'phone'),
                                 ("last_name", 'first_name', 'amount_order'), ('middle_name', 'email'),
                                 ("created_date", 'updated_date'),
                                 ('address', 'delivery'),
                                 ('buyer_comment', 'seller_comment'),
                                 ('comment', )]}),
    )
    ordering = ('-created_date', 'user')

    def number_order(self, obj):
        return obj.pk

    number_order.short_description = _('Order number')

    def amount_order(self, obj):
        return obj.fullamount

    amount_order.short_description = _('Amount')


@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ("user", "zipcode", 'city', "street", 'house_number', 'last_name', 'first_name')
    fieldsets = (
        (_("Delivery Address"), {"fields": [('user',),
                                            ("last_name", 'first_name', 'middle_name'),
                                            ('country', 'region'),
                                            ("zipcode", 'city', 'street'),
                                            ('house_number', 'building', 'flat_number'),
                                            ('phone', 'skype')]}),)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("name", "email", 'created_date', "ip", 'user_agent')
    fieldsets = (
        (_("Feedback"), {"fields": [('name', 'email'), ('message',), ('answer',),
                                    ('created_date', 'ip', 'user_agent'), ]}),
    )
    ordering = ('-created_date', 'name', 'email')
    readonly_fields = ('ip', 'user_agent', 'created_date')


@admin.register(ShopCallback)
class ShopCallbackAdmin(admin.ModelAdmin):
    list_display = ("clientname", "clientphone", 'created_date', 'closed', 'quickorder', "ip", 'user_agent')
    fieldsets = (
        (_("Shop Callback"), {"fields": [('clientname', 'clientphone'), ('created_date', 'closed', 'quickorder'),
                                         ('description',), ('ip', 'user_agent'), ]}),
    )
    ordering = ('-created_date', 'clientname', 'clientphone')
    readonly_fields = ('ip', 'user_agent', 'created_date')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'slide_thumbnail', 'created_date', 'visible', 'vip', "ip", 'user_agent', "user")
    fieldsets = (
        (_("Review"), {"fields": [('name', 'w_position', 'visible'), ('vip', 'img'), ('message',),
                                  ('created_date', 'ip', 'user_agent'), ('user',)]}),
    )
    ordering = ('-created_date', 'user', 'visible')
    readonly_fields = ('ip', 'user_agent', 'created_date')


@admin.register(ShopSlider)
class ShopSliderAdmin(admin.ModelAdmin):
    list_display = ('pk', 'slide_thumbnail', 'slider_link', 'visible')
    fieldsets = (
        (_("ShopSlider"), {"fields": [('img',), ('visible', 'slider_link')]}),
    )
    ordering = ('visible',)


@admin.register(SpecialOffer)
class SpecialOfferAdmin(admin.ModelAdmin):
    class Media:
        js = ['/static/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
              '/static/grappelli/tinymce_setup/tinymce_setup.js', ]

    list_display = ("title", 'start_date', 'end_date', 'slide_thumbnail', 'enabled')
    fieldsets = (
        (_("SpecialOffer"), {"fields": [('title',), ('start_date', 'end_date'),
                                        ('enabled', 'slug', 'position'), ('img',), ('text',)]}),
    )
    ordering = ('-start_date', '-end_date')


@admin.register(ShopNews)
class ShopNewsAdmin(admin.ModelAdmin):
    list_display = ("title", 'created_date')
    fieldsets = (
        (_("Shop News"), {"fields": [('title',), ('created_date', 'enabled'), ('teaser',), ('content', )]}),)
    ordering = ('-created_date', 'title')


@admin.register(ShopArticle)
class ShopArticleAdmin(admin.ModelAdmin):
    list_display = ("title", 'created_date')
    fieldsets = (
        (_("Shop Articles"), {"fields": [('title',), ('created_date', 'enabled'), ('teaser',), ('content', )]}), )
    ordering = ('-created_date', 'title')


@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(admin.ModelAdmin):
    list_display = ("name", "amount", 'enabled_for_registered', 'enabled_for_unregistered', 'position')
    fieldsets = (
        (_("Delivery Method"), {"fields": [('name', 'amount'), ('enabled_for_registered', 'enabled_for_unregistered'),
                                           ('position',), ]}),
    )
    ordering = ('position', 'name')


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(TreeAdmin):
    pass

    class Media:
        js = ['/static/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
              '/static/grappelli/tinymce_setup/tinymce_setup.js', ]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    readonly_fields = ('created_date', 'updated_date')
    list_display = ("name", "category", "created_date", 'amount', 'shop_pn', 'vendor_pn', 'visible')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (_("Service"), {"fields": [('name', 'category'),
                                   ('slug', 'visible', 'avail'),
                                   ('amount', 'teaser'),
                                   ('description',),
                                   ("created_date", 'updated_date'),
                                   ('shop_pn', 'vendor_pn'),
                                   ('position', 'enabled', 'on_main'),
                                   ('discount', 'discount_percent', 'special_offer'),
                                   ('related_services',)]}),)
