# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from nnmware.apps.transport.models import VehicleColor, VehicleKind, VehicleTransmission, VehicleCarcass, \
    VehicleEngine, VehicleFeature, VehicleMark, VehicleVendor, Vehicle
from nnmware.core.admin import ColorAdmin


class VehicleBaseParamAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'slug')
    fieldsets = (
        (_('Type of vehicle'), {"fields": [('name', 'position'),
                                ('description',)]}),
        (_("English"), {"classes": ("collapse",),
                        "fields": [("name_en",), ("description_en",), ]}),)
    ordering = ('position', 'name',)


@admin.register(VehicleKind)
class VehicleKindAdmin(VehicleBaseParamAdmin):
    pass


class VehicleBaseParamForAdmin(VehicleBaseParamAdmin):
    fieldsets = (
        (_('Type of vehicle'), {"fields": [('name', 'position'), ('type_vehicles', ), ('description',)]}),
        (_("English"), {"classes": ("collapse",), "fields": [("name_en",), ("description_en",), ]}),)


@admin.register(VehicleTransmission)
class VehicleTransmissionAdmin(VehicleBaseParamForAdmin):
    pass


@admin.register(VehicleCarcass)
class VehicleCarcassAdmin(VehicleBaseParamForAdmin):
    pass


@admin.register(VehicleEngine)
class VehicleEngineAdmin(VehicleBaseParamForAdmin):
    pass


@admin.register(VehicleFeature)
class VehicleFeatureAdmin(VehicleBaseParamForAdmin):
    pass


@admin.register(VehicleMark)
class VehicleMarkAdmin(VehicleBaseParamForAdmin):
    pass


@admin.register(VehicleVendor)
class VehicleVendorAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('Vendor'), {'fields': [('name', 'country', 'website'), ('description',)]}),
        (_('English'), {'fields': [('name_en', )]}),
    )
    list_display = ('name', 'country', 'website')


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'slug')
    fieldsets = (
        (_('Vehicle'), {"fields": [('name', 'position'),
                                ('description',),
            ('kind', 'color'), ('transmission', 'carcass'),
            ('engine', 'vendor'), ('mileage', 'vin', 'mark'),
            ('horsepower', 'displacement'), ('year', 'left_control'),
            ('features', )]}),
        (_("Seller"), {"classes": ("collapse",),
            "fields": [('user', 'company', 'corporate'), ('contact_name', 'contact_email'),
                       ('contact_phone', ), ('expiration_date', 'sold')]}),
        (_("English"), {"classes": ("collapse",),
            "fields": [("name_en",), ("description_en",), ]}),)
    ordering = ('position', 'name',)


@admin.register(VehicleColor)
class VehicleColorAdmin(ColorAdmin):
    pass
