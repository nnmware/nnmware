from django.contrib import admin
from nnmware.apps.address.models import *
from django.utils.translation import ugettext_lazy as _


class CityAdmin(admin.ModelAdmin):
    list_display = ('name','region','country')
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
    list_display = ('__unicode__',)
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
        (_("Tourism category"), {"fields": [("name",),
            ('description',)]}),
        (_("Addons"), {"fields": [( 'enabled'),
        ]}),
        (_("English"), {"classes": ("collapse closed",),
                        "fields": [("name_en",),("description_en",) , ]}),)



admin.site.register(City, CityAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(TourismCategory, TourismCategoryAdmin)