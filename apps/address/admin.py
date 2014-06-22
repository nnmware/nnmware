from django.contrib import admin
from nnmware.apps.address.models import *
from django.utils.translation import ugettext_lazy as _
from nnmware.core.admin import TypeBaseAdmin


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'country', 'slug', 'longitude', 'latitude')
    search_fields = ('name',)
    fieldsets = (
        (_("City"), {"fields": [("name", "slug"),
            ('description',),
            ('country', 'region'),
            ('longitude', 'latitude'),
            ('name_add', 'order_in_list', 'enabled'),
        ]}),
        (_("English"), {"classes": ("grp-collapse grp-closed",),
                        "fields": [("name_en", "name_add_en"), ("description_en",)]}),)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)
    search_fields = ('name',)
    fieldsets = (
        (_("Region"), {"fields": [("name", "slug", 'country'),
            ('description',),
            ('name_add', 'order_in_list', 'enabled'),
        ]}),
        (_("English"), {"classes": ("grp-collapse grp-closed",),
                        "fields": [("name_en", "name_add_en"), ("description_en",)]}),)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'slug')
    search_fields = ('name',)
    fieldsets = (
        (_("Country"), {"fields": [("name", "slug"),
            ('description', ),
            ('name_add', 'order_in_list', 'enabled'),
        ]}),
        (_("English"), {"classes": ("grp-collapse grp-closed",),
                        "fields": [("name_en", "name_add_en"), ("description_en",)]}),)


@admin.register(TourismCategory)
class TourismCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_en')
    search_fields = ('name',)
    fieldsets = (
        (_("Tourism place category"), {"fields": [("name",),
            ('description',)]}),
        (_("Addons"), {"fields": [('enabled', ), ('icon', ), ]}),
        (_("English"), {"classes": ("grp-collapse grp-closed",),
                        "fields": [("name_en",), ("description_en",), ]}),)


@admin.register(Tourism)
class TourismAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'country', 'city', 'address')
    search_fields = ('name',)
    fieldsets = (
        (_("Tourism place category"), {"fields": [("name", 'address'), ('category',),
            ('description',)]}),
        (_("Addons"), {"fields": [('enabled', 'country', 'city')]}),
        (_("English"), {"classes": ("grp-collapse grp-closed",),
                        "fields": [("name_en", ), ("description_en", )]}),)


@admin.register(StationMetro)
class StationMetroAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    fieldsets = (
        (_("Station of metro"), {"fields": [("name", 'address'),
            ('description',)]}),
        (_("Addons"), {"fields": [('enabled', 'country', 'city'), ]}),
        (_("English"), {"classes": ("grp-collapse grp-closed",),
                        "fields": [("name_en",), ("description_en",)]}),)


@admin.register(Institution)
class InstitutionAdmin(TypeBaseAdmin):
    fieldsets = (
        (_("Institution"), {"fields": [('name', 'order_in_list'),
                                       ('city', 'country')]}),)
