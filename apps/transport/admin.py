# -*- coding: utf-8 -*-
from django.contrib import admin
from nnmware.apps.transport.models import VehicleColor

from nnmware.core.admin import ColorAdmin

admin.site.register(VehicleColor, ColorAdmin)
