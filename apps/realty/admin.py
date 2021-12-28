# nnmware(c)2012-2020

from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import gettext as _

from nnmware.apps.realty.models import Compass, MaterialKind, EstateType, EstateFeature, TrimKind, RmFeature, RmType, \
    Rm, Estate


@admin.register(Compass)
class CompassAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_en', 'abbreviation')
    search_fields = ('name', )
    list_filter = ('name', )
    ordering = ('name', 'name_en')
    fieldsets = (
        (_("Point of compass"), {"fields": [('name', 'abbreviation'), ('name_en',)]}),
    )


@admin.register(MaterialKind)
class MaterialKindAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_en', 'enabled')
    search_fields = ('name', )
    list_filter = ('name', )
    ordering = ('name', 'name_en')
    fieldsets = (
        (_("Material kind"), {"fields": [('name', 'enabled'), ('name_en',)]}),
    )


@admin.register(EstateType)
class EstateTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_en', 'enabled')
    search_fields = ('name', )
    list_filter = ('name', )
    ordering = ('name', 'name_en')
    fieldsets = (
        (_("Estate type"), {"fields": [('name', 'enabled'), ('name_en',)]}),
    )


@admin.register(EstateFeature)
class EstateFeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_en', 'enabled', 'internal', 'external')
    search_fields = ('name', )
    list_filter = ('name', )
    ordering = ('name', 'name_en')
    fieldsets = (
        (_("Estate feature"), {"fields": [('name', 'enabled'), ('internal', 'external'), ('name_en',)]}),
    )


@admin.register(TrimKind)
class TrimKindAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_en', 'enabled', 'internal', 'external')
    search_fields = ('name', )
    list_filter = ('name', )
    ordering = ('name', 'name_en')
    fieldsets = (
        (_("Trim kind"), {"fields": [('name', 'enabled'), ('internal', 'external'), ('name_en',)]}),
    )


@admin.register(RmFeature)
class RmFeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_en', 'enabled', 'internal', 'external')
    search_fields = ('name', )
    list_filter = ('name', )
    ordering = ('name', 'name_en')
    fieldsets = (
        (_("Rm feature"), {"fields": [('name', 'enabled'), ('internal', 'external'), ('name_en',)]}),
    )


@admin.register(RmType)
class RmTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_en', 'enabled', 'internal', 'external')
    search_fields = ('name', )
    list_filter = ('name', )
    ordering = ('name', 'name_en')
    fieldsets = (
        (_("Rm type"), {"fields": [('name', 'enabled'), ('internal', 'external'), ('name_en',)]}),
    )


class RmInline(admin.StackedInline):
    model = Rm
    extra = 0
    fieldsets = (
        (_("Rm's"), {"fields": [
            ('name', 'enabled'),
            ('kind', 'size'),
            ('features', 'description')
        ]}),
    )


@admin.register(Estate)
class EstateAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'company', 'enabled', 'housing')
    fieldsets = (
        (_('Estate'), {"fields": [
            ("name", 'construction_year', 'housing'), ('gross_size', 'live_size'),
            ('user', 'company'),
            ('kind', 'rent', ),
            ('latitude', 'longitude', 'location_public'),
            ('materials', 'features'),
            ('interior', 'exterior'),
            ('total_room', 'floor', 'total_floor'),
            ('description', ),
            ('amount', 'cost_meter'),
            ('created_date', 'updated_date'),
            ('compass', 'contact_name',), ('contact_email', 'contact_phone')
        ]}),
        (_("Address"), {"classes": ("collapse",), "fields": [('country', 'region'), ('city', 'stationmetro'),
                                                             ('zipcode', 'street'), ('house_number', 'building'),
                                                             ('flat_number', )]}),
        (_("English"), {"classes": ("collapse",), "fields": [("name_en", ), ("description_en",)]})
    )
    ordering = ('-created_date', 'name')
    inlines = [RmInline, ]
