# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation.trans_real import get_language
from nnmware.core.fields import std_text_field
from nnmware.core.maps import Geocoder, osm_geocoder
from nnmware.core.abstract import AbstractName

class Address(AbstractName):
    name_add = models.CharField(max_length=100, blank=True)
    name_add_en = models.CharField(max_length=100, blank=True)
    objects = models.Manager()

    class Meta:
        ordering = ['name']
        abstract = True


    def __unicode__(self):
        return self.name

    @property
    def get_name_add(self):
        try:
            if get_language() == 'en':
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



class City(Address):
    longitude = models.FloatField(_('Longitude'), default=0.0)
    latitude = models.FloatField(_('Latitude'), default=0.0)
    region = models.ForeignKey(Region, blank=True, null=True)
    country = models.ForeignKey(Country, blank=True, null=True)

    class Meta:
        unique_together = (('name', 'region'),)
        verbose_name = _("City")
        verbose_name_plural = _("Cities")

    def fulladdress(self):
        if self.country:
            return "%s, %s" % self.name, self.country.name
        return self.name

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
        if not self.latitude and not self.longitude:
            self.fill_osm_data()
        super(City, self).save(*args, **kwargs)

    def fill_osm_data(self):
        response = osm_geocoder(self.geoaddress())[0]
        if response is not None:
            self.longitude = response['lon']
            self.latitude = response['lat']

class AbstractGeo(models.Model):
    longitude = models.FloatField(_('Longitude'), default=0.0)
    latitude = models.FloatField(_('Latitude'), default=0.0)
    city = models.ForeignKey(City, verbose_name=_('City'))
    address = models.CharField(verbose_name=_("Address"), max_length=100, blank=True)
    address_en = models.CharField(verbose_name=_("Address(English)"), max_length=100, blank=True)

    class Meta:
        abstract = True

    def geoaddress(self):
        result = self.address
        addr = result.split(',')
        try:
            r = int(addr[1])
            result = "%s %s" % (addr[1], addr[0])
        except :
            pass
        return u"%s, %s" % (result, self.city)

    def fill_osm_data(self):
        response = osm_geocoder(self.geoaddress())[0]
        if response is not None:
            self.longitude = response['lon']
            self.latitude = response['lat']

    def save(self, *args, **kwargs):
        if not self.latitude and not self.longitude:
            self.fill_osm_data()
        super(AbstractGeo, self).save(*args, **kwargs)

    def fulladdress(self):
        return u"%s, %s" % (self.address, self.city)




class TourismCategory(AbstractName):
    icon = models.ImageField(upload_to="ico/", blank=True, null=True)

    class Meta:
        verbose_name = _("Tourism Place Category")
        verbose_name_plural = _("Tourism Places Categories")
        ordering = ['order_in_list',]


class Tourism(Address, AbstractGeo):
    category = models.ForeignKey(TourismCategory, verbose_name=_('Tourism category'))
    country = models.ForeignKey(Country, blank=True, null=True, verbose_name=_('Country'), on_delete=models.SET_NULL)

    class Meta:
        unique_together = (('name', 'country'),)
        verbose_name = _("Tourism")
        verbose_name_plural = _("Tourism")

    def __unicode__(self):
        return u"%s :: %s" % (self.name, self.country)

    def save(self, *args, **kwargs):
        if not self.slug:
            if not self.pk:
                super(Tourism, self).save(*args, **kwargs)
            self.slug = self.pk
        else:
            if Tourism.objects.filter(slug=self.slug).exclude(pk=self.pk).count():
                self.slug = self.pk
        super(Tourism, self).save(*args, **kwargs)

class StationMetro(Address, AbstractGeo):
    country = models.ForeignKey(Country, verbose_name=_('Country'))

    class Meta:
        unique_together = (('name', 'city'),)
        verbose_name = _("Station of metro")
        verbose_name_plural = _("Stations of metro")

    def __unicode__(self):
        return u"%s :: %s" % (self.name, self.city)

class AbstractLocation(models.Model):
    country = models.ForeignKey(Country, verbose_name=_('Country'), blank=True, null=True)
    city = models.ForeignKey(City, verbose_name=_('City'), blank=True, null=True)
    stationmetro = models.ForeignKey(StationMetro, verbose_name=_('Station of metro'),
        null=True,blank=True, related_name='metro')
    zipcode = models.CharField(max_length=20,verbose_name=_('Zipcode'), blank=True, null=True)
    street = std_text_field(_('Street'))
    house_number = models.CharField(verbose_name=_('Number of house'),max_length=5, blank=True, null=True)
    building = models.CharField(max_length=5,verbose_name=_('Building'), blank=True, null=True)
    flat_number = models.CharField(max_length=5, verbose_name=_('Number of flat'), blank=True, null=True)

    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")
        abstract = True
