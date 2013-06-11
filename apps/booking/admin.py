# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminTimeWidget
from nnmware.apps.booking.models import *
from django.utils.translation import ugettext_lazy as _


class HotelAdminForm(forms.ModelForm):
    class Meta:
        model = Hotel
        widgets = {
            'time_on': AdminTimeWidget(),
            'time_off': AdminTimeWidget()
        }


class AgentPercentInline(admin.StackedInline):
    model = AgentPercent
    extra = 0
    fields = (('date', 'percent'),)


class HotelAdmin(admin.ModelAdmin):
    form = HotelAdminForm
    list_display = ('name', 'register_date', 'city', 'address', 'contact_email', 'contact_name', 'room_count',
                    'starcount', 'enabled', 'point')
    list_filter = ('name', 'starcount', 'city')
    search_fields = ('name',)
    inlines = [AgentPercentInline, ]
    filter_horizontal = ['option', 'admins']
    fieldsets = (
        (_("Hotel"), {"fields": [("name", "slug"), ('city', 'address'), ('description',),
                                 ('room_count', 'starcount'), ('best_offer', 'in_top10', 'work_on_request'),
                                 ('longitude', 'latitude'), 'schema_transit'
        ]}),
        (_("Contacts"), {"fields": [('phone', 'fax'), ('website', 'register_date'), ('contact_email', 'contact_name'),
        ]}),
        (_("Booking"), {"classes": ("grp-collapse grp-closed",), "fields": [('payment_method',), ('booking_terms',),
                                                                            ('condition_cancellation',),
                                                                            ('paid_services',), ('time_on', 'time_off')
        ]}),
        (_("Hotel admins"), {"classes": ("grp-collapse grp-closed",), "fields": [
            ('admins',)]}),
        (_("Hotel options"), {"classes": ("grp-collapse grp-closed",), "fields": [
            ('option',)]}),
        (_("English"), {"classes": ("grp-collapse grp-closed",),
                        "fields": [("name_en", "address_en"), ("description_en",),
                                   ("schema_transit_en",), ("booking_terms_en",)]})
        ,)
    ordering = ('-register_date', 'name')


class HotelOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'in_search', 'sticky_in_search', 'order_in_list')
    list_filter = ('name', 'category', 'in_search', 'sticky_in_search')
    search_fields = ('name',)
    fieldsets = (
        (_("Hotel Option"), {"fields": [("name",),
                                        ('description',)]}),
        (_("Addons"), {"fields": [('category', 'order_in_list'), ( 'enabled', 'in_search', 'sticky_in_search'), ]}),
        (_("English"), {"classes": ("grp-collapse grp-closed",),
                        "fields": [("name_en",), ("description_en",), ]}),)

#    ordering = ('category','order_in_list','name')


class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'places', 'hotel')
    search_fields = ('name',)
    fieldsets = (
        (_("Room"), {"fields": [("name", 'hotel'), ("typefood", 'places'),
                                ('description',)]}),
        (_("English"), {"classes": ("grp-collapse grp-closed",),
                        "fields": [("name_en",), ("description_en",), ]}),)


class RoomOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'order_in_list')
    search_fields = ('name',)
    fieldsets = (
        (_("Room Option"), {"fields": [("name",),
                                       ('description',)]}),
        (_("Addons"), {"fields": [('category', 'slug'), ('enabled', 'order_in_list'), ]}),
        (_("English"), {"classes": ("grp-collapse grp-closed",),
                        "fields": [("name_en",), ("description_en",), ]}),)
    ordering = ('category', 'order_in_list', 'name')


class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    fieldsets = (
        (_("Payment method"), {"fields": [("name", 'use_card'),
                                          ('description',)]}),
        (_("English"), {"classes": ("grp-collapse grp-closed",),
                        "fields": [("name_en",), ("description_en",), ]}),)


class HotelTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    fieldsets = (
        (_("Hotel type"), {"fields": [("name", ), ('description',)]}),
        (_("English"), {"classes": ("grp-collapse grp-closed",),
                        "fields": [("name_en",), ("description_en",), ]}),)


class RoomOptionCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_en', 'enabled', 'slug')
    search_fields = ('name',)
    fieldsets = (
        (_("Room Option Category"), {"fields": [("name", 'slug'),
                                                ('description',)]}),
        (_("Addons"), {"fields": [('order_in_list',), ('enabled',), ]}),
        (_("English"), {"classes": ("grp-collapse grp-closed",), "fields": [("name_en",), ("description_en",), ]}),)


class HotelOptionCategoryAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)
    search_fields = ('name',)
    fieldsets = (
        (_("Hotel Option Category"), {"fields": [("name", 'slug'),
                                                 ('description',)]}),
        (_("Addons"), {"fields": [('order_in_list',), ('enabled',), ('icon',), ]}),
        (_("English"), {"classes": ("grp-collapse grp-closed",),
                        "fields": [("name_en",), ("description_en",), ]}),)


class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'from_date', 'to_date', 'settlement', 'amount', 'currency', 'status', 'date', 'uuid',
        'enabled')
    search_fields = ('from_date',)
    readonly_fields = ('uuid', 'ip', 'user_agent', 'currency', 'settlement', 'hotel')
    fieldsets = (
        (_("Booking Event"), {"fields": [("user", 'status'),
                                         ('from_date', 'to_date'),
                                         ('settlement', 'hotel'),
                                         ('last_name', 'first_name'), ('middle_name', 'date'),
                                         ('phone', 'email'),
                                         ('amount', 'currency'),
                                         ('commission', 'hotel_sum'),
                                         ('uuid', 'enabled'),
                                         ('ip', 'user_agent')]}),
        (_("Credit card"), {"classes": ("grp-collapse grp-closed",), "fields": [("card_number", 'card_valid'),
                                                                                ('card_holder', 'card_cvv2')]}),
    )
    no_root_fieldsets = (
        (_("Booking Event"), {"fields": [("user", 'status'),
                                         ('from_date', 'to_date'),
                                         ('settlement', 'hotel'),
                                         ('last_name', 'first_name'), ('middle_name', 'date'),
                                         ('phone', 'email'),
                                         ('amount', 'currency'),
                                         ('commission', 'hotel_sum'),
                                         ('uuid', 'enabled'),
                                         ('ip', 'user_agent')]}),
    )

    def get_fieldsets(self, request, obj=None):
        if request.user.username != 'root':
            return self.no_root_fieldsets
        return self.fieldsets


class RequestAddHotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'register_date', 'city', 'address', 'phone', 'fax', 'contact_email', 'website')
    search_fields = ('date', 'name')
    fieldsets = (
        (_("Request for add Hotel"), {"fields": [("name", 'register_date'),
                                                 ('city', 'address'),
                                                 ('phone', 'fax'),
                                                 ('email', 'contact_email'),
                                                 ('website', 'rooms_count')]}),)


class AgentPercentAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'city_of_hotel', 'date', 'percent')
    search_fields = ('date', 'percent', 'hotel__name')
    list_filter = ('date', 'hotel', 'percent')
    fieldsets = (
        (_("Agent Percent"), {"fields": [("hotel", 'date', 'percent'), ]}),)

    def city_of_hotel(self, obj):
        return '%s' % obj.hotel.city

    city_of_hotel.short_description = _('City')
    ordering = ('-date',)


class DiscountAdmin(admin.ModelAdmin):
    list_display = ('room', 'date', 'discount')
    search_fields = ('date',)
    fieldsets = (
        (_("Discount"), {"fields": [("room", 'date', 'discount'), ]}),)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)
    search_fields = ('date',)


class SettlementVariantAdmin(admin.ModelAdmin):
    list_display = ('room', 'settlement', 'enabled')
    search_fields = ('date',)
    fieldsets = (
        (_("Settlement Variant"), {"fields": [("room", 'settlement'), ]}),)


class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('room', 'date', 'placecount')
    search_fields = ('date',)
    fieldsets = (
        (_("Availability"), {"fields": [("room", 'date', 'placecount')]}),)


class PlacePriceAdmin(admin.ModelAdmin):
    list_display = ('settlement', 'date', 'amount', 'currency')
    search_fields = ('date',)
    fieldsets = (
        (_("Place Price"), {"fields": [("settlement", 'date'),
                                       ('amount', 'currency')]}),)
    ordering = ('amount',)


admin.site.register(Hotel, HotelAdmin)
admin.site.register(HotelOption, HotelOptionAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(RoomOption, RoomOptionAdmin)
admin.site.register(RoomOptionCategory, RoomOptionCategoryAdmin)
admin.site.register(HotelOptionCategory, HotelOptionCategoryAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(AgentPercent, AgentPercentAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Availability, AvailabilityAdmin)
admin.site.register(RequestAddHotel, RequestAddHotelAdmin)
admin.site.register(SettlementVariant, SettlementVariantAdmin)
admin.site.register(PlacePrice, PlacePriceAdmin)
admin.site.register(PaymentMethod, PaymentMethodAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(HotelType, HotelTypeAdmin)
