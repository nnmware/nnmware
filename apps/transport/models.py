# nnmware(c)2012-2020

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from nnmware.apps.address.models import Country
from nnmware.core.abstract import AbstractName, AbstractVendor, AbstractImg, AbstractDate
from nnmware.core.utils import current_year, tuplify


class VehicleColor(AbstractName):
    pass


class VehicleKind(AbstractName):
    pass

    class Meta:
        verbose_name = _('Vehicle type')
        verbose_name_plural = _('Vehicle types')


class VehicleTransmission(AbstractName):
    pass

    class Meta:
        verbose_name = _('Transmission type')
        verbose_name_plural = _('Transmission types')


class VehicleEngine(AbstractName):
    pass

    class Meta:
        verbose_name = _('Vehicle engine model')
        verbose_name_plural = _('Vehicle engine models')


class VehicleFeature(AbstractName):
    pass

    class Meta:
        verbose_name = _('Vehicle feature')
        verbose_name_plural = _('Vehicle features')


class VehicleVendor(AbstractVendor, AbstractImg):
    country = models.ForeignKey(Country, verbose_name=_('Country'), null=True, blank=True, on_delete=models.SET_NULL)


class VehicleMark(AbstractName):
    vendor = models.ForeignKey(VehicleVendor, verbose_name=_('Vendor of vehicle'), null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = _('Vehicle mark')
        verbose_name_plural = _('Vehicle mark')


VEHICLE_YEAR = map(tuplify, range(current_year - 55, current_year + 1))

