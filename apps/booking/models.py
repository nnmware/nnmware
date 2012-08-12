# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.db.models import permalink, signals, Avg
from django.db.models.manager import Manager
from django.utils.translation import ugettext_lazy as _
from django.utils.translation.trans_real import get_language
from nnmware.apps.address.models import MetaGeo
from nnmware.core.models import Pic
from nnmware.apps.money.models import MoneyBase
from nnmware.apps.address.models import Tourism
from nnmware.core.abstract import MetaIP, MetaName
from nnmware.core.maps import places_near_object

class HotelPoints(models.Model):
    food = models.DecimalField(verbose_name=_('Food'), default=0, decimal_places=1, max_digits=4)
    service = models.DecimalField(verbose_name=_('Service'), default=0, decimal_places=1, max_digits=4)
    purity = models.DecimalField(verbose_name=_('Purity'), default=0, decimal_places=1, max_digits=4)
    transport = models.DecimalField(verbose_name=_('Transport'), default=0, decimal_places=1, max_digits=4)
    prices = models.DecimalField(verbose_name=_('Prices'), default=0, decimal_places=1, max_digits=4)

    class Meta:
        abstract = True


class HotelOptionCategory(MetaName):
    icon = models.ImageField(upload_to="ico/", blank=True, null=True)

    class Meta:
        verbose_name = _("Hotel Option Category")
        verbose_name_plural = _("Hotel Option Categories")
        ordering = ['order_in_list',]

class HotelOption(MetaName):
    category = models.ForeignKey(HotelOptionCategory,verbose_name=_('Category option'))
    in_search = models.BooleanField(verbose_name=_("In search form?"), default=False)
    sticky_in_search = models.BooleanField(verbose_name=_("Sticky in search form?"), default=False)

    class Meta:
        verbose_name = _("Hotel Option")
        verbose_name_plural = _("Hotel Options")
        ordering = ['category', 'order_in_list', 'name' ]

    def __unicode__(self):
        if self.category:
            return _("%(name)s :: %(category)s") % { 'name': self.name, 'category':self.category.name }
        else:
            return _("%(name)s") % { 'name': self.name}

class PaymentMethod(MetaName):
    use_card = models.BooleanField(verbose_name=_("Use credit card?"), default=False)

    class Meta:
        verbose_name = _("Payment method")
        verbose_name_plural = _("Payment methods")
        ordering = ("name",)


UNKNOWN_STAR = -10
HOSTEL = -1
MINI_HOTEL = 0
ONE_STAR = 1
TWO_STAR = 2
THREE_STAR = 3
FOUR_STAR = 4
FIVE_STAR = 5

STAR_CHOICES = (
    (UNKNOWN_STAR, _("Unknown")),
    (HOSTEL, _("Hostel")),
    (MINI_HOTEL, _("Mini-hotel")),
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


class Hotel(MetaName, MetaGeo, HotelPoints):
    register_date = models.DateTimeField(_("Register from"), default=datetime.now())
    email = models.EmailField(verbose_name=_("Email"), blank=True)
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
    best_offer = models.BooleanField(verbose_name=_("Best offer"), default=False)
    in_top10 = models.BooleanField(verbose_name=_("In top 10"), default=False)
    current_amount = models.DecimalField(verbose_name=_('Current amount'), default=0, max_digits=20, decimal_places=3)
    booking_terms = models.TextField(verbose_name=_("Booking terms"), blank=True, null=True)
    schema_transit = models.TextField(verbose_name=_("Schema of transit"), blank=True, null=True)
    booking_terms_en = models.TextField(verbose_name=_("Booking terms(English)"), blank=True, null=True)
    schema_transit_en = models.TextField(verbose_name=_("Schema of transit(English)"), blank=True, null=True)
    payment_method = models.ManyToManyField(PaymentMethod, verbose_name=_('Payment methods'), null=True, blank=True)
    updated_date = models.DateTimeField(_("Updated date"), null=True, blank=True)
    condition_cancellation = models.TextField(verbose_name=_("Condition cancellation"), blank=True, null=True)
    paid_services = models.TextField(verbose_name=_("Paid services"), blank=True, null=True)
    time_on = models.CharField(max_length=5, verbose_name=_('Time on'), blank=True)
    time_off = models.CharField(max_length=5, verbose_name=_('Time off'), blank=True)


    class Meta:
        verbose_name = _("Hotel")
        verbose_name_plural = _("Hotels")
        ordering = ("name",)

    objects = Manager()

    def get_address(self):
        if get_language() == 'en':
            if self.address_en:
                return self.address_en
            else:
                return self.address
        return self.address

    def get_count_stars_hotels(self):
        qs = Hotel.objects.filter(city=self.city)
        two = qs(starcount=TWO_STAR).count()
        three = qs(starcount=THREE_STAR).count()
        four = qs(starcount=FOUR_STAR).count()
        five = qs(starcount=FIVE_STAR).count()
        return [two,three,four,five]

    def fulladdress(self):
        return u"%s, %s" % (self.address, self.city.name)

    def in_city(self):
        return Hotel.objects.filter(city=self.city).count()

    def in_system(self):
        return Hotel.objects.all().count()

    def stars(self):
        if self.starcount == -10:
            return None
        elif self.starcount == -1:
            return 'hostel'
        elif not self.starcount:
            return 'mini'
        else:
            return range(0,int(self.starcount))

    @permalink
    def get_absolute_url(self):
        return "hotel_detail", (), {'city':self.city.slug ,'slug': self.slug}

    @permalink
    def get_cabinet_url(self):
        return "cabinet_info", (), {'city':self.city.slug ,'slug': self.slug}

    def get_current_percent(self):
        try:
            return AgentPercent.objects.filter(hotel=self).filter(date__lte=datetime.now()).order_by('-date')[0].percent
        except IndexError:
            return None

    def get_percent_on_date(self, date):
        return AgentPercent.objects.filter(hotel=self).filter(date__lte=date).order_by('-date')[0].percent

    def free_room(self, from_date, to_date, roomcount):
        result = []
        for room in self.room_set.all():
            check_date = from_date
            avail = None
            while check_date < to_date:
                places = room.date_place_count(check_date)
                if places < roomcount:
                    avail = None
                    break
                avail = 1
                check_date +=timedelta(days=1)
            if avail:
                result.append(room)
        return result


    @property
    def min_current_amount(self):
        rooms = Room.objects.filter(hotel=self)
        result = None
        for r in rooms:
            min_price = r.min_current_amount
            if not result:
                result = min_price
            else:
                if result > min_price > 0:
                    result = min_price
        return result

    def amount_on_date(self, date):
        rooms = Room.objects.filter(hotel=self)
        result = None
        for r in rooms:
            min_price = r.amount_on_date(date)
            if not result:
                result = min_price
            else:
                if result > min_price:
                    result = min_price
        return result


    def save(self, *args, **kwargs):
        if not self.slug:
            if not self.pk:
                super(Hotel, self).save(*args, **kwargs)
            self.slug = self.pk
        else:
            self.slug = self.slug.strip().replace(' ','-')
            if Hotel.objects.filter(slug=self.slug, city=self.city).exclude(pk=self.pk).count():
                self.slug = self.pk
        self.updated_date = datetime.now()
        super(Hotel, self).save(*args, **kwargs)

    def update_hotel_amount(self):
        amount = self.min_current_amount
        if amount:
            self.current_amount = amount
        else:
            self.current_amount = 0
        self.save()

    def tourism_places(self):
        places = Tourism.objects.raw(places_near_object(self,settings.TOURISM_PLACES_RADIUS,
            'address_tourism'))
        all_places = []
        for p in places:
            all_places.append(p.id)
        return Tourism.objects.filter(pk__in=all_places).order_by('category')

    def complete_booking_users_id(self):
        # TODO Check status of bookings
        users_id = Booking.objects.filter(hotel=self).values_list('user',flat=True)
        return users_id

class RoomOptionCategory(MetaName):

    class Meta:
        verbose_name = _("Room Option Category")
        verbose_name_plural = _("Room Option Categories")

class RoomOption(MetaName):
    category = models.ForeignKey(RoomOptionCategory, verbose_name=_("Category"))
    in_search = models.BooleanField(verbose_name=_("In search form?"), default=False)

    class Meta:
        ordering = ['order_in_list', 'name' ]
        verbose_name = _("Room Option")
        verbose_name_plural = _("Room Options")

    def __unicode__(self):
        if self.category:
            return _("%(name)s :: %(category)s") % { 'name': self.name, 'category':self.category.name }
        else:
            return _("%(name)s") % { 'name': self.name}



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

    objects = Manager()

    def __unicode__(self):
        return _("%(room)s :: %(places)s :: %(hotel)s") % { 'room': self.get_name, 'places':self.places, 'hotel':self.hotel.get_name }

    @property
    def min_current_amount(self):
        settlements = SettlementVariant.objects.filter(room=self, enabled=True)
        result = None
        for s in settlements:
            s_min_price = s.current_amount()
            if not result:
                result = s_min_price
            else:
                if result > s_min_price:
                    result = s_min_price
        return result

    def amount_on_date(self, date, guests=None):
        if guests:
            settlements = SettlementVariant.objects.filter(room=self, enabled=True, settlement=guests)
        else:
            settlements = SettlementVariant.objects.filter(room=self, enabled=True)
        result = None
        for s in settlements:
            s_min_price = s.amount_on_date(date)
            if not result:
                result = s_min_price
            else:
                if result > s_min_price:
                    result = s_min_price
        return result

    def amount_on_date_guest_variant(self, date, guests):
        # Find all settlement variants for room
        try:
            s = SettlementVariant.objects.filter(room=self, enabled=True, settlement=guests)[0]
        except :
            try:
                s = SettlementVariant.objects.filter(room=self,
                    enabled=True, settlement__gte=guests).order_by('settlement')[0]
            except :
                s = SettlementVariant.objects.filter(room=self,
                    enabled=True, settlement__lte=guests).order_by('-settlement')[0]
        return s.amount_on_date(date),s.settlement

    def active_settlements(self):
        return SettlementVariant.objects.filter(room=self,enabled=True).order_by('settlement')

    def date_place_count(self,date):
        try:
            places = SettlementVariant.objects.filter(room=self,enabled=True).order_by('-settlement')
            places_max = places[0].settlement
            availability = Availability.objects.get(room=self,date=date).placecount
            return places_max*availability
        except :
            return None

    @permalink
    def get_absolute_url(self):
        return "room_detail", (), {'city':self.hotel.city.slug ,'slug': self.hotel.slug,'pk':self.pk}



class SettlementVariant(models.Model):
    room = models.ForeignKey(Room, verbose_name=_('Room'))
    settlement = models.PositiveSmallIntegerField(_("Settlement"))
    enabled = models.BooleanField(verbose_name=_('Enabled'), default=True)

    class Meta:
        verbose_name = _("Settlement Variant")
        verbose_name_plural = _("Settlements Variants")

    def __unicode__(self):
        return _("Settlement -> %(settlement)s in %(room)s :: %(places)s :: %(hotel)s") % {
            'settlement': self.settlement, 'room': self.room.get_name, 'places':self.room.places,
            'hotel':self.room.hotel.get_name }

    def current_amount(self):
        result = PlacePrice.objects.filter(settlement=self, date__lte=datetime.now()).order_by('-date')
        if result:
            return result[0].amount
        else:
            return 0

    def amount_on_date(self, date):
        result = PlacePrice.objects.filter(settlement=self, date__lte=date).order_by('-date')
        if result:
            return result[0].amount
        else:
            return 0

    @property
    def min_current_amount(self):
        return self.current_amount()


STATUS_UNKNOWN = 0
STATUS_ACCEPTED = 1
STATUS_PRE_CONFIRMED = 2
STATUS_CONFIRMED = 3
STATUS_PAID = 4
STATUS_CANCELED = 5
STATUS_COMPLETED = 6

STATUS_CHOICES = (
    (STATUS_UNKNOWN, _("Unknown")),
    (STATUS_ACCEPTED, _("Accepted")),
    (STATUS_PRE_CONFIRMED, _("Pre-confirmed")),
    (STATUS_CONFIRMED, _("Confirmed")),
    (STATUS_PAID, _("Paid")),
    (STATUS_CANCELED, _("Cancelled")),
    (STATUS_COMPLETED, _("Completed")),
    )

class Booking(MoneyBase, MetaIP):
    user = models.ForeignKey(User, verbose_name=_('User'), blank=True, null=True)
    date = models.DateTimeField(verbose_name=_("Creation date"), default=datetime.now())
    from_date = models.DateField(_("From"))
    to_date = models.DateField(_("To"))
    settlement = models.ForeignKey(SettlementVariant, verbose_name=_('Settlement Variant'), null=True, on_delete=models.SET_NULL)
    hotel = models.ForeignKey(Hotel, verbose_name=_('Hotel'), blank=True, null=True, on_delete=models.SET_NULL)
    status = models.IntegerField(_("Booking status"), choices=STATUS_CHOICES, default=STATUS_UNKNOWN)
    first_name = models.CharField(verbose_name=_("First name"), max_length=100)
    middle_name = models.CharField(verbose_name=_("Middle name"), max_length=100, blank=True)
    last_name = models.CharField(verbose_name=_("Last name"), max_length=100)
    phone = models.CharField(max_length=100, verbose_name=_('Phone'), blank=True)
    email = models.EmailField(_('E-mail'), blank=True)
    uuid = models.CharField(verbose_name=_("Unique ID"), max_length=64, blank=True, null=True, editable=False)
    commission = models.DecimalField(verbose_name=_('Commission'), default=0, max_digits=20, decimal_places=3)
    hotel_sum = models.DecimalField(verbose_name=_('Hotel Sum'), default=0, max_digits=20, decimal_places=3)
    card_number = models.CharField(verbose_name=_("Card number"), max_length=16, blank=True)
    card_valid = models.CharField(verbose_name=_("Card valid to"), max_length=5, blank=True)
    card_holder = models.CharField(verbose_name=_("Card holder"), max_length=50, blank=True)
    card_cvv2 = models.CharField(verbose_name=_("Card verification value(CVV2)"), max_length=4, blank=True)
    payment_method = models.ForeignKey(PaymentMethod, verbose_name=_('Payment method'))

    class Meta:
        ordering = ("-date",)
        verbose_name = _("Booking")
        verbose_name_plural = _("Bookings")

    def __unicode__(self):
         return u"Booking - %s" % self.pk

    @property
    def days(self):
        return (self.to_date-self.from_date).days

    @permalink
    def get_absolute_url(self):
        if not self.uuid:
            self.save()
        return 'booking_hotel_detail', (), { 'slug': self.uuid}

    @permalink
    def get_client_url(self):
        if not self.uuid:
            self.save()
        return 'booking_user_detail', (), { 'slug': self.uuid}


    @property
    def days(self):
        delta = self.to_date-self.from_date
        return delta.days

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid4()
        super(Booking, self).save(*args, **kwargs)


class AgentPercent(models.Model):
    hotel = models.ForeignKey(Hotel)
    date = models.DateField(verbose_name=_("From date"))
    percent = models.DecimalField(verbose_name=_('Percent'), blank=True, decimal_places=1, max_digits=4, default=0)

    class Meta:
        verbose_name = _("Agent Percent")
        verbose_name_plural = _("Agent Percents")

    objects = Manager()

    def __unicode__(self):
        return _("For %(hotel)s on date %(date)s percent is %(percent)s") % \
               { 'hotel': self.hotel.name,
                 'date':self.date,
                 'percent':self.percent }


class Review(MetaIP, HotelPoints):
    user = models.ForeignKey(User)
    hotel = models.ForeignKey(Hotel, blank=True, null=True, on_delete=models.SET_NULL)
    date = models.DateTimeField(verbose_name=_("Published by"), default=datetime.now())
    review = models.TextField(verbose_name=_("Review"),blank=True)

    class Meta:
        ordering = ['-date', ]
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


class RequestAddHotel(MetaIP):
    user = models.ForeignKey(User, verbose_name=_('User'), blank=True, null=True)
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
    starcount = models.IntegerField(_("Count of Stars"), choices=STAR_CHOICES, default=UNKNOWN_STAR)

    class Meta:
        verbose_name = _("Request for add hotel")
        verbose_name_plural = _("Requests for add hotels")
        ordering = ("-pk",)

def update_hotel_point(sender, instance, **kwargs):
    hotel = instance.hotel
    all_points = Review.objects.filter(hotel=hotel).aggregate(Avg('food'), Avg('service'),
        Avg('purity'), Avg('transport'), Avg('prices'))
    hotel.food = Decimal(str(all_points['food__avg'])).quantize(Decimal('1.0'))
    hotel.service = Decimal(str(all_points['service__avg'])).quantize(Decimal('1.0'))
    hotel.purity = Decimal(str(all_points['purity__avg'])).quantize(Decimal('1.0'))
    hotel.transport = Decimal(str(all_points['transport__avg'])).quantize(Decimal('1.0'))
    hotel.prices = Decimal(str(all_points['prices__avg'])).quantize(Decimal('1.0'))
    h_point = (hotel.food+hotel.service+hotel.purity+hotel.transport+hotel.prices)/5
    hotel.point = h_point
    hotel.save()


signals.post_save.connect(update_hotel_point, sender=Review, dispatch_uid="nnmware_id")
signals.post_delete.connect(update_hotel_point, sender=Review, dispatch_uid="nnmware_id")


