# nnmware(c)2012-2020

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation.trans_real import get_language

from nnmware.core.fields import std_text_field
from nnmware.core.maps import osm_geocoder
from nnmware.core.abstract import AbstractName, upload_images_path


class Address(AbstractName):
    name_add = models.CharField(max_length=100, blank=True)
    name_add_en = models.CharField(max_length=100, blank=True)
    objects = models.Manager()

    class Meta:
        ordering = ['name']
        abstract = True

    def __str__(self):
        return self.name

    @property
    def get_name_add(self):
        # noinspection PyBroadException
        try:
            if get_language() == 'en':
                if self.name_add_en:
                    return self.name_add_en
        except:
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
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.CASCADE)

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


class MetaGeo(models.Model):
    longitude = models.FloatField(_('Longitude'), default=0.0, db_index=True)
    latitude = models.FloatField(_('Latitude'), default=0.0, db_index=True)

    class Meta:
        abstract = True

    def fill_osm_data(self):
        response = osm_geocoder(self.geoaddress())
        if response is not None:
            self.longitude = response['lon']
            self.latitude = response['lat']

    def save(self, *args, **kwargs):
        if not self.latitude and not self.longitude:
            self.fill_osm_data()
        super(MetaGeo, self).save(*args, **kwargs)


class City(Address, MetaGeo):
    region = models.ForeignKey(Region, blank=True, null=True, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.CASCADE)
    time_offset = models.SmallIntegerField(verbose_name=_('Time offset from Greenwich'),
                                           choices=[(i, i) for i in range(-11, 13)], default=0)

    class Meta:
        unique_together = (('name', 'region'),)
        verbose_name = _("City")
        verbose_name_plural = _("Cities")

    def fulladdress(self):
        if self.country is not None:
            return "%s, %s" % (self.name, self.country)
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
        super(City, self).save(*args, **kwargs)


class AbstractGeo(MetaGeo):
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.CASCADE)
    address = std_text_field(_("Address"), max_length=100)
    address_en = std_text_field(_("Address(English)"), max_length=100)

    class Meta:
        abstract = True

    def geoaddress(self):
        result = self.address
        addr = result.split(',')
        # noinspection PyBroadException
        try:
            result = "%s %s" % (addr[1], addr[0])
        except:
            pass
        return "%s, %s" % (result, self.city)

    def fulladdress(self):
        return "%s, %s" % (self.address, self.city)


class TourismCategory(AbstractName):
    icon = models.ImageField(upload_to=upload_images_path, blank=True)

    class Meta:
        verbose_name = _("Tourism Place Category")
        verbose_name_plural = _("Tourism Places Categories")
        ordering = ['position', ]


class Tourism(Address, AbstractGeo):
    category = models.ForeignKey(TourismCategory, verbose_name=_('Tourism category'), null=True, on_delete=models.SET_NULL)
    country = models.ForeignKey(Country, blank=True, null=True, verbose_name=_('Country'), on_delete=models.SET_NULL)

    class Meta:
        unique_together = (('name', 'country'),)
        verbose_name = _("Tourism")
        verbose_name_plural = _("Tourism")

    def __str__(self):
        return "%s :: %s" % (self.name, self.country)

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
    country = models.ForeignKey(Country, verbose_name=_('Country'),on_delete=models.CASCADE)

    class Meta:
        unique_together = (('name', 'city'),)
        verbose_name = _("Station of metro")
        verbose_name_plural = _("Stations of metro")

    def __str__(self):
        return "%s :: %s" % (self.name, self.city)


class AbstractLocation(models.Model):
    country = models.ForeignKey(Country, verbose_name=_('Country'), blank=True, null=True,
                                related_name="%(class)s_cou", on_delete=models.CASCADE)
    region = models.ForeignKey(Region, verbose_name=_('Region'), blank=True, null=True,
                               related_name="%(class)s_reg", on_delete=models.CASCADE)
    city = models.ForeignKey(City, verbose_name=_('City'), blank=True, null=True,
                             related_name="%(class)s_cit", on_delete=models.CASCADE)
    stationmetro = models.ForeignKey(StationMetro, verbose_name=_('Station of metro'),  null=True,
                                    blank=True, related_name='%(class)s_metro', on_delete=models.CASCADE)
    zipcode = models.CharField(max_length=20, verbose_name=_('Zipcode'), blank=True)
    street = std_text_field(_('Street'))
    house_number = std_text_field(_('Number of house'), max_length=5)
    building = std_text_field(_('Building'), max_length=5)
    flat_number = std_text_field(_('Number of flat'), max_length=5)

    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")
        abstract = True

    def geoaddress(self):
        # noinspection PyBroadException
        try:
            return "%s %s, %s" % (self.house_number, self.street, self.city)
        except:
            return None

    @property
    def get_fulladdress(self):
        result = ''
        if self.country:
            result += self.country.get_name + ', '
        if self.region:
            result += self.region.get_name + ', '
        if self.city:
            result += self.city.get_name + ', '
        if self.street:
            result += self.street + ' '
        if self.house_number:
            result += self.house_number + ' '
        if self.building:
            result += self.building + ' '
        if self.flat_number:
            result += self.flat_number
        return result


class Institution(AbstractName):
    city = models.ForeignKey(City, verbose_name=_('City'), related_name='edu_city', null=True,
                             blank=True, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, verbose_name=_('Country'), related_name='edu_country',
                                null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Institution")
        verbose_name_plural = _("Institutions")

    def __str__(self):
        return "%s" % self.name
