# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.address.models import Country
from nnmware.core.abstract import AbstractColor, AbstractName, AbstractVendor, AbstractDate
from nnmware.apps.business.models import AbstractSeller


class VehicleColor(AbstractColor):
    pass


class VehicleType(AbstractName):
    pass

    class Meta:
        verbose_name = _('Vehicle type')
        verbose_name_plural = _('Vehicle types')


class VehicleTransmission(AbstractName):
    type_vehicles = models.ManyToManyField(VehicleType, verbose_name=_('Using in vehicles'), blank=True, null=True)

    class Meta:
        verbose_name = _('Transmission type')
        verbose_name_plural = _('Transmission types')


class VehicleCarcass(AbstractName):
    type_vehicles = models.ManyToManyField(VehicleType, verbose_name=_('Using in vehicles'), blank=True, null=True)

    class Meta:
        verbose_name = _('Vehicle carcass type')
        verbose_name_plural = _('Vehicle carcass types')


class VehicleEngine(AbstractName):
    type_vehicles = models.ManyToManyField(VehicleType, verbose_name=_('Using in vehicles'), blank=True, null=True)

    class Meta:
        verbose_name = _('Vehicle carcass type')
        verbose_name_plural = _('Vehicle carcass types')


class VehicleVendor(AbstractVendor):
    country = models.ForeignKey(Country, verbose_name=_('Country'), null=True, blank=True, on_delete=models.SET_NULL)


class Vehicle(AbstractName, AbstractDate, AbstractSeller):
    pass
