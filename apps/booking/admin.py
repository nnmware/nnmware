from django.contrib import admin
from nnmware.apps.booking.models import *
from django.utils.translation import ugettext_lazy as _


class HotelAdmin(admin.ModelAdmin):
    list_display = ('name','register_date','city','address','contact_email','contact_name','room_count','starcount','point')
    search_fields = ('name',)
    fieldsets = (
        (_("Hotel"), {"fields": [("name","slug"),('city','address'),
            ('description',),
            ('room_count','starcount')
        ]}),
        (_("Contacts"), {"fields": [('phone', 'fax'),('website','register_date'), ( 'contact_email','contact_name'),
        ]}),
        (_("Hotel options and admins"), {"classes": ("collapse closed",), "fields": [
            ('option','admins')
        ]}),
        (_("English"), {"classes": ("collapse closed",),
                        "fields": [("name_en","address_en"),("description_en",) ]}),)


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
        (_("Addons"), {"fields": [('order_in_list' ), ( 'enabled',),
        ]}),
        (_("English"), {"classes": ("collapse closed",),
                        "fields": [("name_en",),("description_en",) , ]}),)

class BookingAdmin(admin.ModelAdmin):
    list_display = ('user','from_date','to_date','room','amount','currency','status','date')
    search_fields = ('from_date',)
    fieldsets = (
        (_("Booking Event"), {"fields": [("user",'room','hotel'),
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
    list_display = ('__unicode__',)
    search_fields = ('date',)
    fieldsets = (
        (_("Agent Percent"), {"fields": [("hotel",'date','percent'),]}),)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)
    search_fields = ('date',)


class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('room','date','amount','currency','roomcount')
    search_fields = ('date',)
    fieldsets = (
        (_("Place Price"), {"fields": [("room",'date'),
            ('amount','currency','roomcount')]}),)




class PlaceCountAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)
    search_fields = ('count',)

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
admin.site.register(PlaceCount, PlaceCountAdmin)
admin.site.register(RequestAddHotel, RequestAddHotelAdmin)


