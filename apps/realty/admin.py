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

admin.site.register(Compass, CompassAdmin)
admin.site.register(MaterialKind, MaterialKindAdmin)
admin.site.register(EstateType, EstateTypeAdmin)
