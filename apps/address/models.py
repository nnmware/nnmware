# -*- coding: utf-8 -*-
from django.conf import settings

from django.db import models
from django.utils.translation import ugettext_lazy as _
from nnmware.core.middleware import get_request
from nnmware.core.models import MetaName, MetaGeo

class Address(MetaName):
    name_add = models.CharField(max_length=100, blank=True)
    name_add_en = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['name']
        abstract = True

    def __unicode__(self):
            return self.name

    def get_name_add(self):
        if get_request().COOKIES[settings.LANGUAGE_COOKIE_NAME] == 'en-en':
            if self.name_add_en:
                return self.name_add_en
        return self.name_add


class Country(Address):

    class Meta:
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")

    def __unicode__(self):
        return self.name


class Region(Address):
    country = models.ForeignKey(Country, null=True, blank=True)

    class Meta:
        unique_together = (('name', 'country'),)
        verbose_name = _("Region")
        verbose_name_plural = _("Regions")

class City(Address, MetaGeo):
    region = models.ForeignKey(Region, blank=True, null=True)
    country = models.ForeignKey(Country, blank=True, null=True)

    class Meta:
        unique_together = (('name', 'region'),)
        verbose_name = _("City")
        verbose_name_plural = _("Cities")

    def fulladdress(self):
        return u"%s" % (self.name)
