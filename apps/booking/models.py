# -*- coding: utf-8 -*-

from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.address.models import City
from nnmware.core.middleware import get_request
from nnmware.core.models import MetaName, MetaGeo
from nnmware.apps.money.models import MoneyBase
from nnmware.apps.address.models import Tourism
from nnmware.apps.booking.managers import SettlementVariantManager

class HotelOptionCategory(MetaName):

    class Meta:
        verbose_name = _("Hotel Option Category")
        verbose_name_plural = _("Hotel Option Categories")
        ordering = ['order_in_list',]

class HotelOption(MetaName):
    category = models.ForeignKey(HotelOptionCategory,verbose_name=_('Category option'), null=True, blank=True, on_delete=models.SET_NULL)
    in_search = models.BooleanField(verbose_name=_("In search form?"), default=False)
    sticky_in_search = models.BooleanField(verbose_name=_("Sticky in search form?"), default=False)

    class Meta:
        verbose_name = _("Hotel Option")
        verbose_name_plural = _("Hotel Options")

    def __unicode__(self):
        return _("%(name)s :: %(category)s") % { 'name': self.name, 'category':self.category.name }

UNKNOWN_STAR = 0
ONE_STAR = 1
TWO_STAR = 2
THREE_STAR = 3
FOUR_STAR = 4
FIVE_STAR = 5

STAR_CHOICES = (
    (UNKNOWN_STAR, _("Unknown")),
    (ONE_STAR, _("One star")),
    (TWO_STAR, _("Two star")),
    (THREE_STAR, _("Three star")),
    (FOUR_STAR, _("Four star")),
    (FIVE_STAR, _("Five star")),
    )

HOTEL_UNKNOWN = 0
HOTEL_HOTEL = 1
HOTEL_COTTAGE = 2
HOTEL_HOME = 3
HOTEL_FLAT = 4

HOTEL_CHOICES = (
    (HOTEL_UNKNOWN, _("Unknown")),
    (HOTEL_HOTEL, _("Hotel")),
    (HOTEL_COTTAGE, _("Cottage")),
    (HOTEL_HOME, _("Home")),
    (HOTEL_FLAT, _("Flat")),
    )


class Hotel(MetaName, MetaGeo):
    register_date = models.DateTimeField(_("Register from"), default=datetime.now())
    city = models.ForeignKey(City, verbose_name=_('City'), null=True, blank=True, on_delete=models.SET_NULL)
    email = models.EmailField(verbose_name=_("Email"), blank=True)
    address = models.CharField(verbose_name=_("Address"), max_length=100, blank=True)
    address_en = models.CharField(verbose_name=_("Address(English)"), max_length=100, blank=True)
    phone = models.CharField(max_length=100, verbose_name=_('Phone'), blank=True)
    fax = models.CharField(max_length=100, verbose_name=_('Fax'), blank=True)
    website = models.URLField(max_length=150, verbose_name=_(u'Website'), blank=True)
    contact_email = models.EmailField(verbose_name=_("Contact Email"), blank=True)
    contact_name = models.CharField(max_length=100, verbose_name=_('Contact Name'), blank=True)
    room_count = models.IntegerField(_('Count of Rooms'), blank=True, default=0)
    option = models.ManyToManyField(HotelOption, verbose_name=_('Hotel Options'),blank=True,null=True)
    starcount = models.IntegerField(_("Count of Stars"), choices=STAR_CHOICES, default=UNKNOWN_STAR)
    choice = models.IntegerField(_("Type of Hotel"), choices=HOTEL_CHOICES, default=HOTEL_HOTEL, editable=False)
    admins = models.ManyToManyField(User, verbose_name=_('Hotel Admins'), null=True, blank=True)
    point = models.DecimalField(_("Point of hotel"), editable=False, default=0, decimal_places=1, max_digits=4)
    food_point = models.DecimalField(verbose_name=_('Food average'), default=0, decimal_places=1, max_digits=4)
    service_point = models.DecimalField(verbose_name=_('Service average'), default=0, decimal_places=1, max_digits=4)
    purity_point = models.DecimalField(verbose_name=_('Purity average'), default=0, decimal_places=1, max_digits=4)
    transport_point = models.DecimalField(verbose_name=_('Transport average'), default=0, decimal_places=1, max_digits=4)
    prices_point = models.DecimalField(verbose_name=_('Prices average'), default=0, decimal_places=1, max_digits=4)
    tourism = models.ManyToManyField(Tourism, verbose_name=_('Tourism places'), null=True, blank=True)


    class Meta:
        verbose_name = _("Hotel")
        verbose_name_plural = _("Hotels")

    def get_address(self):
        if get_request().COOKIES[settings.LANGUAGE_COOKIE_NAME] == 'en-en':
            if self.address_en:
                return self.address_en
        return self.name

    def get_count_stars_hotels(self):
        qs = Hotel.objects.filter(city=self.city)
        two = qs(starcount=TWO_STAR).count()
        three = qs(starcount=THREE_STAR).count()
        four = qs(starcount=FOUR_STAR).count()
        five = qs(starcount=FIVE_STAR).count()
        return [two,three,four,five]

    def is_admin(self):
        if get_request().user in self.admins:
            return True
        return False

    def fulladdress(self):
        return u"%s, %s" % (self.city.name, self.address)

    def in_city(self):
        return Hotel.objects.filter(city=self.city).count()

    def stars(self):
        return range(0,self.starcount)

    @permalink
    def get_absolute_url(self):
        return "hotel_detail", (), {'slug': self.slug}

    def get_current_percent(self):
        return AgentPercent.objects.filter(hotel=self).filter(date__lte=datetime.now()).order_by('-date')[0].percent

    def free_room(self, from_date, to_date, roomcount, with_child=None):
        d = to_date-from_date
        delta = d.days+1
        result = []
        for room in self.room_set.all():
            avail = Availability.objects.filter(room=room, placecount__gte=roomcount,
                date__range=(from_date,to_date)).count()
            if avail == delta:
                result.append(room)
        return result

class RoomOptionCategory(MetaName):

    class Meta:
        verbose_name = _("Room Option Category")
        verbose_name_plural = _("Room Option Categories")

class RoomOption(MetaName):
    category = models.ForeignKey(RoomOptionCategory, null=True, blank=True, on_delete=models.SET_NULL)
    in_search = models.BooleanField(verbose_name=_("In search form?"), default=False)

    class Meta:
        verbose_name = _("Room Option")
        verbose_name_plural = _("Room Options")

    def __unicode__(self):
        return _("%(name)s :: %(category)s") % { 'name': self.name, 'category':self.category.name }


PLACES_UNKNOWN = 0
PLACES_ONE = 1
PLACES_TWO = 2
PLACES_THREE = 3
PLACES_FOUR = 4
PLACES_FIVE = 5
PLACES_SIX = 6
PLACES_SEVEN = 7
PLACES_EIGHT = 8

PLACES_CHOICES = (
    (PLACES_UNKNOWN, _("Unknown")),
    (PLACES_ONE, _("One")),
    (PLACES_TWO, _("Two")),
    (PLACES_THREE, _("Three")),
    (PLACES_FOUR, _("Four")),
    (PLACES_FIVE, _("Five")),
    (PLACES_SIX, _("Six")),
    (PLACES_SEVEN, _("Seven")),
    (PLACES_EIGHT, _("Eight")),
    )


class Room(MetaName):
    option = models.ManyToManyField(RoomOption, verbose_name=_('Availability options'),blank=True,null=True)
    hotel = models.ForeignKey(Hotel, verbose_name=_('Hotel'), null=True, blank=True, on_delete=models.SET_NULL)
    places = models.IntegerField(_("Place Count"), choices=PLACES_CHOICES, default=PLACES_UNKNOWN)

    class Meta:
        verbose_name = _("Room")
        verbose_name_plural = _("Rooms")

    def __unicode__(self):
        return _("%(room)s :: %(places)s :: %(hotel)s") % { 'room': self.get_name(), 'places':self.places, 'hotel':self.hotel.get_name() }

    def min_current_amount(self):
        settlements = SettlementVariant.objects.filter(room=self)
        result = None
        for s in settlements:
            s_min_price = s.current_amount()
            if not result:
                result = s_min_price
            else:
                if result > s_min_price:
                    result = s_min_price
        return result

class SettlementVariant(models.Model):
    room = models.ForeignKey(Room, verbose_name=_('Room'))
    settlement = models.PositiveSmallIntegerField(_("Settlement"))
    enabled = models.BooleanField(verbose_name=_('Enabled'), default=True)

    class Meta:
        verbose_name = _("Settlement Variant")
        verbose_name_plural = _("Settlements Variants")

    objects = SettlementVariantManager()

    def __unicode__(self):
        return _("Settlement -> %(settlement)s in %(room)s :: %(places)s :: %(hotel)s") % {
            'settlement': self.settlement, 'room': self.room.get_name(), 'places':self.room.places,
            'hotel':self.room.hotel.get_name() }

    def current_amount(self):
        result = PlacePrice.objects.filter(settlement=self,
            date__lte=datetime.now()).order_by('-date')
        if result:
            return result[0].amount
        else:
            return 0

STATUS_UNKNOWN = 0
STATUS_ACCEPTED = 1
STATUS_PAID = 2
STATUS_CANCELED = 3

STATUS_CHOICES = (
    (STATUS_UNKNOWN, _("Unknown")),
    (STATUS_ACCEPTED, _("Accepted")),
    (STATUS_PAID, _("Paid")),
    (STATUS_CANCELED, _("Cancelled")),
    )

class Booking(MoneyBase):
    user = models.ForeignKey(User, verbose_name=_('User'), blank=True, null=True)
    date = models.DateTimeField(verbose_name=_("Creation date"), default=datetime.now())
    from_date = models.DateField(_("From"))
    to_date = models.DateField(_("To"))
    settlement = models.ForeignKey(SettlementVariant, verbose_name=_('Settlement Variant'), on_delete=models.SET_NULL)
    hotel = models.ForeignKey(Hotel, verbose_name=_('Hotel'), blank=True, null=True, on_delete=models.SET_NULL)
    status = models.IntegerField(_("Booking status"), choices=STATUS_CHOICES, default=STATUS_UNKNOWN)
    first_name = models.CharField(verbose_name=_("First name"), max_length=100)
    middle_name = models.CharField(verbose_name=_("Middle name"), max_length=100, blank=True)
    last_name = models.CharField(verbose_name=_("Last name"), max_length=100)
    phone = models.CharField(max_length=100, verbose_name=_('Phone'), blank=True)
    email = models.EmailField(_('E-mail'), blank=True)


    class Meta:
        ordering = ("-date",)
        verbose_name = _("Booking")
        verbose_name_plural = _("Bookings")

    def __unicode__(self):
         return u"Booking - %s" % self.pk

class AgentPercent(models.Model):
    hotel = models.ForeignKey(Hotel, blank=True, null=True, on_delete=models.SET_NULL)
    date = models.DateField(verbose_name=_("From date"))
    percent = models.DecimalField(verbose_name=_('Percent'), blank=True, decimal_places=1, max_digits=4, default=0)

    class Meta:
        verbose_name = _("Agent Percent")
        verbose_name_plural = _("Agent Percents")

    def __unicode__(self):
        return _("For %(hotel)s on date %(date)s percent is %(percent)s") % \
               { 'hotel': self.hotel.name,
                 'date':self.date,
                 'percent':self.percent }

class Review(models.Model):
    user = models.ForeignKey(User)
    hotel = models.ForeignKey(Hotel, blank=True, null=True, on_delete=models.SET_NULL)
    date = models.DateTimeField(verbose_name=_("Published by"), default=datetime.now())
    review = models.TextField(verbose_name=_("Review"),blank=True)
    food = models.DecimalField(verbose_name=_('Food'), default=0, decimal_places=1, max_digits=4)
    service = models.DecimalField(verbose_name=_('Service'), default=0, decimal_places=1, max_digits=4)
    purity = models.DecimalField(verbose_name=_('Purity'), default=0, decimal_places=1, max_digits=4)
    transport = models.DecimalField(verbose_name=_('Transport'), default=0, decimal_places=1, max_digits=4)
    prices = models.DecimalField(verbose_name=_('Prices'), default=0, decimal_places=1, max_digits=4)

    class Meta:
        verbose_name = _("Client review")
        verbose_name_plural = _("Client reviews")

    def __unicode__(self):
        return _("Review client %(client)s for hotel %(hotel)s is -> %(review)s") % \
               { 'client': self.user.get_full_name(),
                 'hotel': self.hotel.name,
                 'review': self.review }

class Availability(models.Model):
    room = models.ForeignKey(Room, verbose_name=_('Room'), null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateField(verbose_name=_("On date"))
    placecount = models.IntegerField(verbose_name=_('Count of places'), default=0)

    class Meta:
        verbose_name = _("Availability Place")
        verbose_name_plural = _("Availabilities Places")

    def __unicode__(self):
        return _("Availability place %(place)s for hotel %(hotel)s on date %(date)s is -> %(count)s")  % \
                { 'place': self.room.name,
                 'hotel': self.room.hotel.name,
                 'date': self.date,
                 'count': self.placecount
               }

class PlacePrice(MoneyBase):
    date = models.DateField(verbose_name=_("On date"))
    settlement = models.ForeignKey(SettlementVariant, verbose_name=_('Settlement Variant'))

    class Meta:
        verbose_name = _("Place Price")
        verbose_name_plural = _("Places Prices")

    def __unicode__(self):
        return _("Price settlement %(settlement)s for hotel %(hotel)s on date %(date)s is -> %(price)s %(currency)s")  %\
               { 'settlement': self.settlement.settlement,
                 'hotel': self.settlement.room.hotel.name,
                 'date': self.date,
                 'price': self.amount,
                 'currency': self.currency.code
               }


class RequestAddHotel(models.Model):
    register_date = models.DateTimeField(_("Register date"), default=datetime.now())
    city = models.CharField(verbose_name=_("City"), max_length=100, null=True, blank=True)
    address = models.CharField(verbose_name=_("Address"), max_length=100, null=True, blank=True)
    name = models.CharField(verbose_name=_("Name"), max_length=100, null=True, blank=True)
    email = models.CharField(verbose_name=_("Email"), max_length=100, null=True, blank=True)
    phone = models.CharField(verbose_name=_("Phone"), max_length=100, null=True, blank=True)
    fax = models.CharField(verbose_name=_("Fax"), max_length=100, null=True, blank=True)
    contact_email = models.CharField(verbose_name=_("Contact email"), max_length=100, null=True, blank=True)
    website = models.CharField(verbose_name=_("Website"), max_length=100, null=True, blank=True)
    rooms_count = models.CharField(verbose_name=_("Count of rooms"), max_length=100, null=True, blank=True)
    ip = models.IPAddressField(verbose_name=_('IP'), null=True, blank=True)
    user_agent = models.CharField(verbose_name=_('User Agent'), null=True, blank=True, max_length=255)

    class Meta:
        verbose_name = _("Request for add hotel")
        verbose_name_plural = _("Requests for add hotels")

    def save(self, *args, **kwargs):
        self.ip = get_request().META['REMOTE_ADDR']
        self.user_agent = get_request().META['HTTP_USER_AGENT']
        super(RequestAddHotel, self).save(*args, **kwargs)
