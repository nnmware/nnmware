# nnmware(c)2012-2017

from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from nnmware.apps.address.models import City, Region, Country, TourismCategory, Tourism, StationMetro, Institution
from nnmware.core.admin import TypeBaseAdmin


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'country', 'slug', 'longitude', 'latitude')
    search_fields = ('name',)
    fieldsets = (
        (_("City"), {"fields": [("name", "slug"), ('description',), ('country', 'region', 'time_offset'),
                                ('longitude', 'latitude'), ('name_add', 'position', 'enabled')]}),
        (_("English"), {"classes": ("collapse",), "fields": [("name_en", "name_add_en"), ("description_en",)]})
    )


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    search_fields = ('name',)
    fieldsets = (
        (_("Region"), {"fields": [("name", "slug", 'country'), ('description',), ('name_add', 'position', 'enabled')]}),
        (_("English"), {"classes": ("collapse",), "fields": [("name_en", "name_add_en"), ("description_en",)]})
    )


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'slug')
    search_fields = ('name',)
    fieldsets = (
        (_("Country"), {"fields": [("name", "slug"), ('description',), ('name_add', 'position', 'enabled')]}),
        (_("English"), {"classes": ("collapse",), "fields": [("name_en", "name_add_en"), ("description_en",)]})
    )


@admin.register(TourismCategory)
class TourismCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_en')
    search_fields = ('name',)
    fieldsets = (
        (_("Tourism place category"), {"fields": [("name",), ('description',)]}),
        (_("Addons"), {"fields": [('enabled', ), ('icon',)]}),
        (_("English"), {"classes": ("collapse",), "fields": [("name_en",), ("description_en",)]})
    )


@admin.register(Tourism)
class TourismAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'country', 'city', 'address')
    search_fields = ('name',)
    fieldsets = (
        (_("Tourism place category"), {"fields": [("name", 'address'), ('category',), ('description',)]}),
        (_("Addons"), {"fields": [('enabled', 'country', 'city')]}),
        (_("English"), {"classes": ("collapse",), "fields": [("name_en", ), ("description_en", )]})
    )


@admin.register(StationMetro)
class StationMetroAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    fieldsets = (
        (_("Station of metro"), {"fields": [("name", 'address'), ('description',)]}),
        (_("Addons"), {"fields": [('enabled', 'country', 'city')]}),
        (_("English"), {"classes": ("collapse",), "fields": [("name_en",), ("description_en",)]})
    )


@admin.register(Institution)
class InstitutionAdmin(TypeBaseAdmin):
    fieldsets = (
        (_("Institution"), {"fields": [('name', 'position'), ('city', 'country')]}),
    )
