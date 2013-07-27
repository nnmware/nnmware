# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from nnmware.apps.transport.models import VehicleColor, VehicleKind
from nnmware.core.admin import ColorAdmin


class VehicleKindAdmin(admin.ModelAdmin):
    list_display = ('name', 'order_in_list', 'slug')
    fieldsets = (
        (_('Type of vehicle'), {"fields": [('name', 'order_in_list'),
                                ('description',)]}),
        (_("English"), {"classes": ("grp-collapse grp-closed",),
                        "fields": [("name_en",), ("description_en",), ]}),)
    ordering = ('-order_in_list', 'name',)


admin.site.register(VehicleColor, ColorAdmin)
admin.site.register(VehicleKind, VehicleKindAdmin)
