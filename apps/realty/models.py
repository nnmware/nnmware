# nnmware(c)2012-2017

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from nnmware.apps.address.models import AbstractLocation, MetaGeo
from nnmware.apps.business.models import AbstractSeller
from nnmware.apps.money.models import MoneyBase
from nnmware.core.abstract import AbstractDate, AbstractName


class Compass(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=100)
    name_en = models.CharField(verbose_name=_('Name(en)'), max_length=100)
    abbreviation = models.CharField(verbose_name=_('Abbreviation'), max_length=2)

    class Meta:
        verbose_name = _("Point of compass")
        verbose_name_plural = _("Points of compass")


class MaterialKind(AbstractName):
    pass

    class Meta:
        verbose_name = _("Material kind")
        verbose_name_plural = _("Materials kinds")


class ExtInt(models.Model):
    internal = models.BooleanField(verbose_name=_("Internal"), default=False)
    external = models.BooleanField(verbose_name=_("External"), default=False)

    class Meta:
        abstract = True


class EstateType(AbstractName):
    pass

    class Meta:
        verbose_name = _("Estate type")
        verbose_name_plural = _("Estate types")


class EstateFeature(AbstractName, ExtInt):
    pass

    class Meta:
        verbose_name = _("Estate feature")
        verbose_name_plural = _("Estate features")


class TrimKind(AbstractName, ExtInt):
    pass

    class Meta:
        verbose_name = _("Trim kind")
        verbose_name_plural = _("Trims kinds")


class Estate(AbstractName, AbstractLocation, MetaGeo, AbstractDate, MoneyBase, AbstractSeller):
    gross_size = models.DecimalField(verbose_name=_('Gross area size (square meters)'), default=0, max_digits=10,
                                     decimal_places=1, db_index=True)
    live_size = models.DecimalField(verbose_name=_('Living space size (square meters)'), default=0, max_digits=10,
                                    decimal_places=1, db_index=True)
    construction_year = models.PositiveSmallIntegerField(verbose_name=_('Date of construction'), blank=True, null=True)
    materials = models.ManyToManyField(MaterialKind, verbose_name=_('Materials kinds'))
    interior = models.ManyToManyField(TrimKind, verbose_name=_('Interior trim kinds'), related_name='int_estate')
    exterior = models.ManyToManyField(TrimKind, verbose_name=_('Exterior trim kinds'), related_name='ext_estate')
    housing = models.BooleanField(verbose_name=_("Housing"), default=False)
    kind = models.ForeignKey(EstateType, verbose_name=_('Estate type'))
    location_public = models.BooleanField(verbose_name=_("Is location public?"), default=False)
    features = models.ManyToManyField(EstateFeature, verbose_name=_('Estate features'))
    total_room = models.PositiveSmallIntegerField(verbose_name=_('Total rooms count'), blank=True, null=True)
    floor = models.PositiveSmallIntegerField(verbose_name=_('Floor'), blank=True, null=True)
    total_floor = models.PositiveSmallIntegerField(verbose_name=_('Total floor'), blank=True, null=True)
    compass = models.ManyToManyField(Compass, verbose_name=_('Points of compass'))
    rent = models.BooleanField(verbose_name=_("Rent"), default=False)
    cost_meter = models.DecimalField(verbose_name=_('Cost per square meter'), default=0, max_digits=20,
                                     decimal_places=3, db_index=True)

    class Meta:
        verbose_name = _("Estate")
        verbose_name_plural = _("Estate")


class RmFeature(AbstractName, ExtInt):
    pass

    class Meta:
        verbose_name = _("Rm feature")
        verbose_name_plural = _("Rm features")


class RmType(AbstractName, ExtInt):
    pass

    class Meta:
        verbose_name = _("Rm type")
        verbose_name_plural = _("Rms types")


class Rm(AbstractName):
    kind = models.ForeignKey(RmType, verbose_name=_('Rm type'))
    estate = models.ForeignKey(Estate, verbose_name=_('Estate'))
    size = models.DecimalField(verbose_name=_('Space size (square meters)'), default=0, max_digits=10,
                               decimal_places=1, db_index=True)
    features = models.ManyToManyField(RmFeature, verbose_name=_('Rm features'))

    class Meta:
        verbose_name = _("Rm")
        verbose_name_plural = _("Rms")
