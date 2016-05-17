# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminTimeWidget
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.booking.models import Hotel, AgentPercent, HotelOption, Room, RoomOption, PaymentMethod, HotelType, \
    RoomOptionCategory, HotelOptionCategory, Booking, RequestAddHotel, Review, SettlementVariant, \
    Availability, PlacePrice, SimpleDiscount, HotelSearch

try:
    from pytils.translit import slugify
except:
    from django.template.defaultfilters import slugify


class HotelAdminForm(forms.ModelForm):

    class Meta:
        model = Hotel
        fields = '__all__'
        widgets = {
            'time_on': AdminTimeWidget(),
            'time_off': AdminTimeWidget()
        }


class AgentPercentInline(admin.StackedInline):
    model = AgentPercent
    extra = 0
    fields = (('date', 'percent'),)


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    form = HotelAdminForm
    list_display = ('name', 'register_date', 'city', 'address', 'contact_email', 'contact_name', 'room_count',
                    'starcount', 'enabled', 'point')
    list_filter = ('name', 'starcount', 'city')
    search_fields = ('name',)
    inlines = [AgentPercentInline, ]
    filter_horizontal = ['option', 'admins']
    readonly_fields = ('translit_name',)

    def translit_name(self, obj):
        return slugify(obj.name)
    translit_name.short_description = 'Translit'

    fieldsets = (
        (_("Hotel"), {"fields": [("name", "slug"), ('city', 'address'), ('translit_name', 'addon_city'),
                                 ('description',),
                                 ('room_count', 'starcount', 'email'), ('best_offer', 'in_top10', 'work_on_request'),
                                 ('longitude', 'latitude'), ('schema_transit',)]}),
        (_("Contacts"), {"fields": [('phone', 'fax'), ('website',), ('contact_email', 'contact_name'),
                                    ('register_date', )]}),
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
                                   ('schema_transit_en',), ("booking_terms_en",),
                                   ('paid_services_en',), ('condition_cancellation_en',)]}),)
    ordering = ('-register_date', 'name')


@admin.register(HotelOption)
class HotelOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'in_search', 'sticky_in_search', 'position')
    list_filter = ('name', 'category', 'in_search', 'sticky_in_search')
    search_fields = ('name',)
    fieldsets = (
        (_("Hotel Option"), {"fields": [("name",),
                                        ('description',)]}),
        (_("Addons"), {"fields": [('category', 'position'), ('enabled', 'in_search', 'sticky_in_search'), ]}),
        (_("English"), {"classes": ("grp-collapse grp-closed",),
                        "fields": [("name_en",), ("description_en",), ]}),)

#    ordering = ('category','position','name')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'places', 'hotel')
    search_fields = ('name',)
    fieldsets = (
        (_("Room"), {"fields": [("name", 'hotel', 'surface_area'), ("typefood", 'places'),
                                ('description',)]}),
        (_("English"), {"classes": ("grp-collapse grp-closed",),
                        "fields": [("name_en",), ("description_en",), ]}),)


@admin.register(RoomOption)
class RoomOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'position')
    search_fields = ('name',)
    fieldsets = (
        (_("Room Option"), {"fields": [("name",),
                                       ('description',)]}),
        (_("Addons"), {"fields": [('category', 'slug'), ('enabled', 'position'), ]}),
        (_("English"), {"classes": ("grp-collapse grp-closed",),
                        "fields": [("name_en",), ("description_en",), ]}),)
    ordering = ('category', 'position', 'name')


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    fieldsets = (
        (_("Payment method"), {"fields": [("name", 'use_card'),
                                          ('description',)]}),
        (_("English"), {"classes": ("grp-collapse grp-closed",),
                        "fields": [("name_en",), ("description_en",), ]}),)


@admin.register(HotelType)
class HotelTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    fieldsets = (
        (_("Hotel type"), {"fields": [("name", ), ('description',)]}),
        (_("English"), {"classes": ("grp-collapse grp-closed",),
                        "fields": [("name_en",), ("description_en",), ]}),)


@admin.register(RoomOptionCategory)
class RoomOptionCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_en', 'enabled', 'slug')
    search_fields = ('name',)
    fieldsets = (
        (_("Room Option Category"), {"fields": [("name", 'slug'),
                                                ('description',)]}),
        (_("Addons"), {"fields": [('position',), ('enabled',), ]}),
        (_("English"), {"classes": ("grp-collapse grp-closed",), "fields": [("name_en",), ("description_en",), ]}),)


@admin.register(HotelOptionCategory)
class HotelOptionCategoryAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    search_fields = ('name',)
    fieldsets = (
        (_("Hotel Option Category"), {"fields": [("name", 'slug'),
                                                 ('description',)]}),
        (_("Addons"), {"fields": [('position',), ('enabled',), ('icon',), ]}),
        (_("English"), {"classes": ("grp-collapse grp-closed",),
                        "fields": [("name_en",), ("description_en",), ]}),)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'from_date', 'to_date', 'settlement', 'guests', 'amount', 'status', 'date',
                    'uuid', 'btype', 'enabled')
    search_fields = ('from_date',)
    readonly_fields = ('uuid', 'ip', 'user_agent', 'currency', 'settlement', 'hotel', 'btype')
    fieldsets = (
        (_("Booking Event"), {"fields": [("user", 'status', 'guests'),
                                         ('from_date', 'to_date', 'cancel_time'),
                                         ('settlement', 'hotel'),
                                         ('last_name', 'first_name'), ('middle_name', 'date'),
                                         ('phone', 'email'),
                                         ('amount', 'currency'),
                                         ('hotel_sum', 'commission'),
                                         ('freecancel', 'penaltycancel'),
                                         ('uuid', 'enabled'),
                                         ('ip', 'user_agent')]}),
        (_("Credit card"), {"classes": ("grp-collapse grp-closed",), "fields": [("card_number", 'card_valid'),
                                                                                ('card_holder', 'card_cvv2')]}),
        (_("Addons"), {"classes": ("grp-collapse grp-closed",),
                       "fields": [('settlement_txt', ), ('hotel_txt', ), ('comment', )]}),
    )
    no_root_fieldsets = (
        (_("Booking Event"), {"fields": [("user", 'status', 'guests'),
                                         ('from_date', 'to_date', 'cancel_time'),
                                         ('settlement', 'hotel'),
                                         ('last_name', 'first_name'), ('middle_name', 'date'),
                                         ('phone', 'email'),
                                         ('amount', 'currency'),
                                         ('hotel_sum', 'commission'),
                                         ('uuid', 'enabled'),
                                         ('ip', 'user_agent')]}),
        (_("Addons"), {"classes": ("grp-collapse grp-closed",),
                       "fields": [('settlement_txt', ), ('hotel_txt', ), ('comment', )]}),
    )

    def get_fieldsets(self, request, obj=None):
        if request.user.username != 'root':
            return self.no_root_fieldsets
        return self.fieldsets


@admin.register(RequestAddHotel)
class RequestAddHotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'register_date', 'city', 'address', 'phone', 'fax', 'contact_email', 'website')
    search_fields = ('date', 'name')
    fieldsets = (
        (_("Request for add Hotel"), {"fields": [("name", 'register_date'),
                                                 ('city', 'address'),
                                                 ('phone', 'fax'),
                                                 ('email', 'contact_email'),
                                                 ('website', 'rooms_count')]}),)


@admin.register(AgentPercent)
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


# @admin.register(Discount)
# TODO Disabled
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'name', 'choice', 'percentage', 'enabled')
    # search_fields = ('date',)
    # readonly_fields = ('hotel', )
    ordering = ('choice', )
    fieldsets = (
        (_("Discount"), {"fields": [('name', "hotel"), ('choice', 'percentage'), ('time_on', 'time_off'),
            ('days', 'at_price_days')]}),)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('__str__', )
    search_fields = ('date',)


@admin.register(SettlementVariant)
class SettlementVariantAdmin(admin.ModelAdmin):
    list_display = ('room', 'settlement', 'enabled')
    search_fields = ('date',)
    fieldsets = (
        (_("Settlement Variant"), {"fields": [("room", 'settlement'), ]}),)


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('room', 'date', 'placecount')
    search_fields = ('date',)
    fieldsets = (
        (_("Availability"), {"fields": [("room", 'date', 'placecount')]}),)


@admin.register(PlacePrice)
class PlacePriceAdmin(admin.ModelAdmin):
    list_display = ('settlement', 'date', 'amount', 'currency')
    search_fields = ('date',)
    fieldsets = (
        (_("Place Price"), {"fields": [("settlement", 'date'), ('amount', 'currency')]}),)
    ordering = ('amount',)


# @admin.register(RoomDiscount)
# TODO Disabled
class RoomDiscountAdmin(admin.ModelAdmin):
    list_display = ('room', 'discount', 'date', 'value')
    search_fields = ('date',)
    fieldsets = (
        (_("Room discount"), {"fields": [("room", 'discount'), ('date', 'value')]}),)
    ordering = ('value',)
    # raw_id_fields = ('room', 'discount')
    # autocomplete_lookup_fields = {'fk': ['room', 'discount']}


@admin.register(SimpleDiscount)
class SimpleDiscountAdmin(admin.ModelAdmin):
    list_display = ('room', 'ub', 'ub_discount', 'gb', 'gb_days', 'gb_penalty', 'gb_discount', 'nr', 'nr_discount')
    search_fields = ('room__name',)
    fieldsets = (
        (_("Room simple discount"), {"fields": [('room', )]}),
        (_("Unguaranteed booking"), {"fields": [('ub', 'ub_discount')]}),
        (_("Guaranteed booking"), {"fields": [('gb', 'gb_days', 'gb_penalty', 'gb_discount')]}),
        (_("Non-return rate"), {"fields": [('nr', 'nr_discount')]}),)
    ordering = ('room',)
    readonly_fields = ('room', )


@admin.register(HotelSearch)
class HotelSearchAdmin(admin.ModelAdmin):
    list_display = ('ip', 'date', 'city', 'hotel', 'from_date', 'to_date', 'guests', 'user_agent')
    search_fields = ('ip', 'city', 'hotel')
    fieldsets = (
        (_("Hotel search"), {"fields": [('ip', 'date'), ('city', 'hotel'), ('from_date', 'to_date'),
                                        ('guests', 'user_agent')]}),)
    ordering = ('date', 'city', 'hotel')
    readonly_fields = ('ip', 'date', 'city', 'hotel', 'from_date', 'to_date', 'guests', 'user_agent')
