# nnmware(c)2012-2020

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from nnmware.apps.transport.models import VehicleColor, VehicleKind, VehicleTransmission, \
    VehicleEngine, VehicleFeature, VehicleMark, VehicleVendor
from nnmware.core.admin import ColorAdmin


class VehicleBaseParamAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'slug')
    fieldsets = (
        (_('Type of vehicle'), {"fields": [('name', 'position'), ('description',)]}),
        (_("English"), {"classes": ("collapse",), "fields": [("name_en",), ("description_en",), ]})
    )
    ordering = ('position', 'name',)


@admin.register(VehicleKind)
class VehicleKindAdmin(VehicleBaseParamAdmin):
    pass


class VehicleBaseParamForAdmin(VehicleBaseParamAdmin):
    fieldsets = (
        (_('Type of vehicle'), {"fields": [('name', 'position'), ('description',)]}),
        (_("English"), {"classes": ("collapse",), "fields": [("name_en",), ("description_en",), ]})
    )


@admin.register(VehicleTransmission)
class VehicleTransmissionAdmin(VehicleBaseParamForAdmin):
    pass


@admin.register(VehicleEngine)
class VehicleEngineAdmin(VehicleBaseParamForAdmin):
    pass


@admin.register(VehicleFeature)
class VehicleFeatureAdmin(VehicleBaseParamForAdmin):
    pass


@admin.register(VehicleMark)
class VehicleMarkAdmin(VehicleBaseParamForAdmin):
    fieldsets = (
        (_('Type of vehicle'), {"fields": [('name', 'position'), ('vendor', ), ('description',)]}),
        (_("English"), {"classes": ("collapse",), "fields": [("name_en",), ("description_en",), ]})
    )
    list_display = ('name', 'position', 'slug', 'vendor')


@admin.register(VehicleVendor)
class VehicleVendorAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('Vendor'), {'fields': [('name', 'country', 'website'), ('description',)]}),
        (_('English'), {'fields': [('name_en', )]})
    )
    list_display = ('name', 'country', 'website')


@admin.register(VehicleColor)
class VehicleColorAdmin(ColorAdmin):
    pass
