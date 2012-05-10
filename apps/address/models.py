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

    @property
    def get_name_add(self):
        try:
            if get_request().COOKIES[settings.LANGUAGE_COOKIE_NAME] == 'en-en':
                if self.name_add_en:
                    return self.name_add_en
        except :
            pass
        if self.name_add:
            return self.name_add
        return self.get_name


class Country(Address):

    class Meta:
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            if not self.pk:
                super(Country, self).save(*args, **kwargs)
            self.slug = self.pk
        else:
            if Country.objects.filter(slug=self.slug).exclude(pk=self.pk).count():
                self.slug = self.pk
        super(Country, self).save(*args, **kwargs)

class Region(Address):
    country = models.ForeignKey(Country, null=True, blank=True)

    class Meta:
        unique_together = (('name', 'country'),)
        verbose_name = _("Region")
        verbose_name_plural = _("Regions")


    def save(self, *args, **kwargs):
        if not self.slug:
            if not self.pk:
                super(Region, self).save(*args, **kwargs)
            self.slug = self.pk
        else:
            if Region.objects.filter(slug=self.slug).exclude(pk=self.pk).count():
                self.slug = self.pk
        super(Region, self).save(*args, **kwargs)


class City(Address, MetaGeo):
    region = models.ForeignKey(Region, blank=True, null=True)
    country = models.ForeignKey(Country, blank=True, null=True)

    class Meta:
        unique_together = (('name', 'region'),)
        verbose_name = _("City")
        verbose_name_plural = _("Cities")

    def fulladdress(self):
        return u"%s" % self.name

    def get_absolute_url(self):
        return 'city_detail', [self.slug]

    def geoaddress(self):
        return self.fulladdress()

    def save(self, *args, **kwargs):
        if not self.slug:
            if not self.pk:
                super(City, self).save(*args, **kwargs)
            self.slug = self.pk
        else:
            if City.objects.filter(slug=self.slug).exclude(pk=self.pk).count():
                self.slug = self.pk
        super(City, self).save(*args, **kwargs)


class TourismCategory(MetaName):
    icon = models.ImageField(upload_to="ico/", blank=True, null=True)

    class Meta:
        verbose_name = _("Tourism Place Category")
        verbose_name_plural = _("Tourism Places Categories")
        ordering = ['order_in_list',]


class Tourism(Address, MetaGeo):
    category = models.ForeignKey(TourismCategory, verbose_name=_('Tourism category'), blank=True, null=True,
        on_delete=models.SET_NULL)
    city = models.ForeignKey(City, blank=True, null=True, verbose_name=_('City'), on_delete=models.SET_NULL)
    country = models.ForeignKey(Country, blank=True, null=True, verbose_name=_('Country'), on_delete=models.SET_NULL)
    address = models.CharField(verbose_name=_("Address"), max_length=100, blank=True)
    address_en = models.CharField(verbose_name=_("Address(English)"), max_length=100, blank=True)

    class Meta:
        unique_together = (('name', 'country'),)
        verbose_name = _("Tourism")
        verbose_name_plural = _("Tourism")

    def __unicode__(self):
        return u"%s :: %s" % (self.name, self.country)

    def fulladdress(self):
        return u"%s, %s" % (self.address, self.city)

    def save(self, *args, **kwargs):
        if not self.slug:
            if not self.pk:
                super(Tourism, self).save(*args, **kwargs)
            self.slug = self.pk
        else:
            if Tourism.objects.filter(slug=self.slug).exclude(pk=self.pk).count():
                self.slug = self.pk
        super(Tourism, self).save(*args, **kwargs)
