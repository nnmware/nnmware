# -*- coding: utf-8 -*-


from django.db import models
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.address.models import AbstractLocation, MetaGeo
from nnmware.apps.money.models import MoneyBase
from nnmware.core.abstract import AbstractData, AbstractDate


class MaterialKind(AbstractData):
    pass

    class Meta:
        verbose_name = _("Material kind")
        verbose_name_plural = _("Materials kinds")


class EstateType(AbstractData):
    pass

    class Meta:
        verbose_name = _("Estate type")
        verbose_name_plural = _("Estate types")


class EstateFeature(AbstractData):
    internal = models.BooleanField(verbose_name=_("Internal"), default=False)
    external = models.BooleanField(verbose_name=_("External"), default=False)

    class Meta:
        verbose_name = _("Estate feature")
        verbose_name_plural = _("Estate features")


class TrimKind(AbstractData):
    internal = models.BooleanField(verbose_name=_("Internal"), default=False)

    class Meta:
        verbose_name = _("Trim kind")
        verbose_name_plural = _("Trims kinds")


class Estate(AbstractData, AbstractLocation, MetaGeo, AbstractDate, MoneyBase):
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

    class Meta:
        verbose_name = _("Estate")
        verbose_name_plural = _("Estate")


class RmFeature(AbstractData):
    internal = models.BooleanField(verbose_name=_("Internal"), default=False)
    external = models.BooleanField(verbose_name=_("External"), default=False)

    class Meta:
        verbose_name = _("Rm feature")
        verbose_name_plural = _("Rm features")


class Rm(AbstractData):
    estate = models.ForeignKey(Estate, verbose_name=_('Estate'))
    size = models.DecimalField(verbose_name=_('Space size (square meters)'), default=0, max_digits=10,
                               decimal_places=1, db_index=True)
    features = models.ManyToManyField(RmFeature, verbose_name=_('Rm features'))

    class Meta:
        verbose_name = _("Rm")
        verbose_name_plural = _("Rms")

