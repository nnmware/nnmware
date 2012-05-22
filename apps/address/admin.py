from django.contrib import admin
from nnmware.apps.address.models import *
from django.utils.translation import ugettext_lazy as _


class CityAdmin(admin.ModelAdmin):
    list_display = ('name','region','country','slug')
    search_fields = ('name',)
    fieldsets = (
        (_("City"), {"fields": [("name","slug"),
            ('description',),
            ('country','region'),
            ('name_add','order_in_list','enabled'),
        ]}),
        (_("English"), {"classes": ("collapse closed",),
                        "fields": [("name_en","name_add_en"),("description_en",) ]}),)


class RegionAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)
    search_fields = ('name',)
    fieldsets = (
        (_("Region"), {"fields": [("name","slug",'country'),
            ('description',),
            ('name_add','order_in_list','enabled'),
        ]}),
        (_("English"), {"classes": ("collapse closed",),
                        "fields": [("name_en","name_add_en"),("description_en",) ]}),)


class CountryAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','slug')
    search_fields = ('name',)
    fieldsets = (
        (_("Country"), {"fields": [("name","slug"),
            ('description',),
            ('name_add','order_in_list','enabled'),
        ]}),
        (_("English"), {"classes": ("collapse closed",),
                        "fields": [("name_en","name_add_en"),("description_en",) ]}),)

class TourismCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_en')
    search_fields = ('name',)
    fieldsets = (
        (_("Tourism place category"), {"fields": [("name",),
            ('description',)]}),
        (_("Addons"), {"fields": [( 'enabled'),( 'icon'),
        ]}),
        (_("English"), {"classes": ("collapse closed",),
                        "fields": [("name_en",),("description_en",) , ]}),)

class TourismAdmin(admin.ModelAdmin):
    list_display = ('name','category' ,'country','city','address')
    search_fields = ('name',)
    fieldsets = (
        (_("Tourism place category"), {"fields": [("name",'address'),('category',),
            ('description',)]}),
        (_("Addons"), {"fields": [( 'enabled','country','city'),
        ]}),
        (_("English"), {"classes": ("collapse closed",),
                        "fields": [("name_en",),("description_en",) , ]}),)

class StationMetroAdmin(admin.ModelAdmin):
    list_display = ('name','country','city','address')
    search_fields = ('name',)
    fieldsets = (
        (_("Station of metro"), {"fields": [("name",'address'),
            ('description',)]}),
#        (_("Addons"), {"fields": [( 'enabled','country','city'),
#        ]}),
#        (_("English"), {"classes": ("collapse closed",),
#                        "fields": [("name_en",),("description_en",) , ]}),
        )

admin.site.register(City, CityAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(TourismCategory, TourismCategoryAdmin)
admin.site.register(Tourism, TourismAdmin)
admin.site.register(StationMetro, StationMetroAdmin)