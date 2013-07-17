# -*- coding: utf-8 -*-

from django.contrib import admin
from nnmware.apps.realty.models import *
from django.utils.translation import ugettext_lazy as _


class CompassAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_en', 'abbreviation')
    search_fields = ('name', )
    list_filter = ('name', )
    ordering = ('name', 'name_en')
    fieldsets = (
        (_("Point of compass"), {"fields": [('name', 'abbreviation'),
            ('name_en', )]}),)


class MaterialKindAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_en', 'enabled')
    search_fields = ('name', )
    list_filter = ('name', )
    ordering = ('name', 'name_en')
    fieldsets = (
        (_("Material kind"), {"fields": [('name', 'enabled'),
            ('name_en', )]}),)


class EstateTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_en', 'enabled')
    search_fields = ('name', )
    list_filter = ('name', )
    ordering = ('name', 'name_en')
    fieldsets = (
        (_("Estate type"), {"fields": [('name', 'enabled'),
            ('name_en', )]}),)


class EstateFeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_en', 'enabled', 'internal', 'external')
    search_fields = ('name', )
    list_filter = ('name', )
    ordering = ('name', 'name_en')
    fieldsets = (
        (_("Estate feature"), {"fields": [('name', 'enabled'), ('internal', 'external'),
            ('name_en', )]}),)


class TrimKindAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_en', 'enabled', 'internal', 'external')
    search_fields = ('name', )
    list_filter = ('name', )
    ordering = ('name', 'name_en')
    fieldsets = (
        (_("Trim kind"), {"fields": [('name', 'enabled'), ('internal', 'external'),
            ('name_en', )]}),)


class RmFeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_en', 'enabled', 'internal', 'external')
    search_fields = ('name', )
    list_filter = ('name', )
    ordering = ('name', 'name_en')
    fieldsets = (
        (_("Rm feature"), {"fields": [('name', 'enabled'), ('internal', 'external'),
            ('name_en', )]}),)


class RmTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_en', 'enabled', 'internal', 'external')
    search_fields = ('name', )
    list_filter = ('name', )
    ordering = ('name', 'name_en')
    fieldsets = (
        (_("Rm type"), {"fields": [('name', 'enabled'), ('internal', 'external'),
            ('name_en', )]}),)


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
        (_("English"), {"classes": ("grp-collapse grp-closed",),
                        "fields": [("name_en", ), ("description_en",)]}))
    ordering = ('-created_date', 'name')


admin.site.register(Compass, CompassAdmin)
admin.site.register(MaterialKind, MaterialKindAdmin)
admin.site.register(EstateType, EstateTypeAdmin)
admin.site.register(EstateFeature, EstateFeatureAdmin)
admin.site.register(TrimKind, TrimKindAdmin)
admin.site.register(RmFeature, RmFeatureAdmin)
admin.site.register(RmType, RmTypeAdmin)
admin.site.register(Estate, EstateAdmin)
