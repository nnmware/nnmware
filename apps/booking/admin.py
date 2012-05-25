# -*- coding: utf-8 -*-
from django.contrib import admin
from nnmware.apps.booking.models import *
from django.utils.translation import ugettext_lazy as _


class HotelAdmin(admin.ModelAdmin):
    list_display = ('name','register_date','city','address','contact_email','contact_name','room_count','starcount','enabled','point')
    list_filter = ('starcount','name')
    search_fields = ('name',)
    filter_horizontal = ['option','admins']
    fieldsets = (
        (_("Hotel"), {"fields": [("name","slug"),('city','address'),
            ('description',),
            ('room_count','starcount'),('best_offer','in_top10'),
            ('longitude','latitude'),
            ('schema_transit')
        ]}),
        (_("Contacts"), {"fields": [('phone', 'fax'),('website','register_date'), ( 'contact_email','contact_name'),
        ]}),
        (_("Booking"), {"classes": ("collapse closed",), "fields": [('payment_method'),('booking_terms')
        ]}),
        (_("Hotel admins"), {"classes": ("collapse closed",), "fields": [
            ('admins')]}),
        (_("Hotel options"), {"classes": ("collapse closed",), "fields": [
            ('option')]}),
        (_("English"), {"classes": ("collapse closed",),
                        "fields": [("name_en","address_en"),("description_en",),
            ("schema_transit_en"),("booking_terms_en")
        ]}),)
    ordering = ('register_date','name')

class HotelOptionAdmin(admin.ModelAdmin):
    list_display = ('name','category','in_search','sticky_in_search')
    search_fields = ('name',)
    fieldsets = (
        (_("Hotel Option"), {"fields": [("name",),
            ('description',)]}),
        (_("Addons"), {"fields": [('category','order_in_list' ), ( 'enabled','in_search','sticky_in_search'),
        ]}),
        (_("English"), {"classes": ("collapse closed",),
                        "fields": [("name_en",),("description_en",) , ]}),)



class RoomAdmin(admin.ModelAdmin):
    list_display = ('name','places','hotel')
    search_fields = ('name',)

class RoomOptionAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)
    search_fields = ('name',)
    fieldsets = (
        (_("Room Option"), {"fields": [("name",),
            ('description',)]}),
            (_("Addons"), {"fields": [('category','slug' ), ( 'enabled','order_in_list'),
            ]}),
            (_("English"), {"classes": ("collapse closed",),
                    "fields": [("name_en",),("description_en",) , ]}),)

class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    fieldsets = (
        (_("Payment method"), {"fields": [("name",),
            ('description',)]}),
        (_("English"), {"classes": ("collapse closed",),
                        "fields": [("name_en",),("description_en",) , ]}),)

class RoomOptionCategoryAdmin(admin.ModelAdmin):
    list_display = ('name','name_en','enabled','slug')
    search_fields = ('name',)
    fieldsets = (
        (_("Room Option Category"), {"fields": [("name",'slug'),
            ('description',)]}),
        (_("Addons"), {"fields": [('order_in_list' ), ( 'enabled',),
        ]}),
        (_("English"), {"classes": ("collapse closed",),
                        "fields": [("name_en",),("description_en",) , ]}),)


class HotelOptionCategoryAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)
    search_fields = ('name',)
    fieldsets = (
        (_("Hotel Option Category"), {"fields": [("name",'slug'),
            ('description',)]}),
        (_("Addons"), {"fields": [('order_in_list' ), ( 'enabled',), ( 'icon',),
        ]}),
        (_("English"), {"classes": ("collapse closed",),
                        "fields": [("name_en",),("description_en",) , ]}),)

class BookingAdmin(admin.ModelAdmin):
    list_display = ('user','from_date','to_date','settlement','amount','currency','status','date','uuid')
    search_fields = ('from_date',)
    fieldsets = (
        (_("Booking Event"), {"fields": [("user",'settlement','hotel'),
            ('from_date','to_date','status'),
            ('amount','currency','date')]}),)

class RequestAddHotelAdmin(admin.ModelAdmin):
    list_display = ('name','register_date','city','address','phone','fax','contact_email','website')
    search_fields = ('date','name')
    fieldsets = (
        (_("Request for add Hotel"), {"fields": [("name",'register_date'),
            ('city','address'),
            ('phone','fax'),
            ('email','contact_email'),
            ('website','rooms_count')]}),)


class AgentPercentAdmin(admin.ModelAdmin):
    list_display = ('hotel','date','percent')
    search_fields = ('date',)
    fieldsets = (
        (_("Agent Percent"), {"fields": [("hotel",'date','percent'),]}),)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)
    search_fields = ('date',)

class SettlementVariantAdmin(admin.ModelAdmin):
    list_display = ('room','settlement','enabled')
    search_fields = ('date',)
    fieldsets = (
        (_("Settlement Variant"), {"fields": [("room",'settlement'),]}),)

class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('room','date','placecount')
    search_fields = ('date',)
    fieldsets = (
        (_("Availability"), {"fields": [("room",'date','placecount')]}),)

class PlacePriceAdmin(admin.ModelAdmin):
    list_display = ('settlement','date','amount','currency')
    search_fields = ('date',)
    fieldsets = (
        (_("Place Price"), {"fields": [("settlement",'date'),
            ('amount','currency')]}),)


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



