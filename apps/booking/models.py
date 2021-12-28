# nnmware(c)2012-2020

from __future__ import unicode_literals

import random
from datetime import timedelta, time, datetime
from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.db.models import signals, Avg, Min, Count
from django.db.models.manager import Manager
from django.template.defaultfilters import date
from django.urls import reverse
from django.utils.text import format_lazy
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django.utils.translation.trans_real import get_language

from nnmware.apps.address.models import AbstractGeo, Tourism, City
from nnmware.apps.money.models import MoneyBase
from nnmware.core.abstract import AbstractIP, AbstractName, AbstractDate, upload_images_path
from nnmware.core.maps import places_near_object


class HotelPoints(models.Model):
    food = models.DecimalField(verbose_name=_('Food'), default=0, decimal_places=1, max_digits=4, db_index=True)
    service = models.DecimalField(verbose_name=_('Service'), default=0, decimal_places=1, max_digits=4, db_index=True)
    purity = models.DecimalField(verbose_name=_('Purity'), default=0, decimal_places=1, max_digits=4, db_index=True)
    transport = models.DecimalField(verbose_name=_('Transport'), default=0, decimal_places=1, max_digits=4,
                                    db_index=True)
    prices = models.DecimalField(verbose_name=_('Prices'), default=0, decimal_places=1, max_digits=4, db_index=True)

    class Meta:
        abstract = True


class HotelOptionCategory(AbstractName):
    icon = models.ImageField(upload_to=upload_images_path, blank=True)

    class Meta:
        verbose_name = _("Hotel Option Category")
        verbose_name_plural = _("Hotel Option Categories")
        ordering = ['position', ]


class HotelOption(AbstractName):
    category = models.ForeignKey(HotelOptionCategory, verbose_name=_('Category option'), on_delete=models.CASCADE)
    in_search = models.BooleanField(verbose_name=_("In search form?"), default=False, db_index=True)
    sticky_in_search = models.BooleanField(verbose_name=_("Sticky in search form?"), default=False, db_index=True)

    class Meta:
        verbose_name = _("Hotel Option")
        verbose_name_plural = _("Hotel Options")
        ordering = ['category', 'position', 'name']

    def __str__(self):
        if self.category:
            return _("%(name)s :: %(category)s") % {'name': self.name, 'category': self.category.name}
        else:
            return _("%(name)s") % {'name': self.name}


class PaymentMethod(AbstractName):
    use_card = models.BooleanField(verbose_name=_("Use credit card?"), default=False, db_index=True)

    class Meta:
        verbose_name = _("Payment method")
        verbose_name_plural = _("Payment methods")
        ordering = ("name",)


class HotelType(AbstractName):
    pass

    class Meta:
        verbose_name = _("Hotel type")
        verbose_name_plural = _("Hotel types")
        ordering = ("name",)


UNKNOWN_STAR = -10
HOSTEL = -2
APARTAMENTS = -1
MINI_HOTEL = 0
ONE_STAR = 1
TWO_STAR = 2
THREE_STAR = 3
FOUR_STAR = 4
FIVE_STAR = 5

STAR_CHOICES = (
    (UNKNOWN_STAR, _("Unknown")),
    (HOSTEL, _("Hostel")),
    (APARTAMENTS, _("Apartaments")),
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

TYPEFOOD_RO = 0
TYPEFOOD_BB = 1
TYPEFOOD_CB = 2
TYPEFOOD_HB = 3
TYPEFOOD_FB = 4
TYPEFOOD_AI = 5
TYPEFOOD_AC = 6
TYPEFOOD_EB = 7
TYPEFOOD_HBPLUS = 8
TYPEFOOD_FBPLUS = 9

TYPEFOOD = (
    (TYPEFOOD_RO, _("RO - Without breakfast")),
    (TYPEFOOD_BB, _("BB - Breakfast")),
    (TYPEFOOD_CB, _("CB - Continental breakfast")),
    (TYPEFOOD_HB, _("HB - Half board (breakfast and lunch/dinner")),
    (TYPEFOOD_FB, _("FB - Full board (breakfast, lunch, dinner)")),
    (TYPEFOOD_AI, _("AI - All included")),
    (TYPEFOOD_AC, _("AC - A la carte (on menu)")),
    (TYPEFOOD_EB, _("EB - English breakfast")),
    (TYPEFOOD_HBPLUS, _("HB+ - Half board + local drinks")),
    (TYPEFOOD_FBPLUS, _("FB+ - Full board + local drinks")),
)


class Hotel(AbstractName, AbstractGeo, HotelPoints):
    register_date = models.DateTimeField(_("Register from"), default=now)
    email = models.CharField(verbose_name=_("Email"), blank=True, max_length=75)
    phone = models.CharField(max_length=100, verbose_name=_('Phone'), blank=True)
    fax = models.CharField(max_length=100, verbose_name=_('Fax'), blank=True)
    website = models.URLField(max_length=150, verbose_name=_('Website'), blank=True)
    contact_email = models.CharField(verbose_name=_("Contact Email"), blank=True, max_length=75)
    contact_name = models.CharField(max_length=100, verbose_name=_('Contact Name'), blank=True)
    room_count = models.IntegerField(_('Count of Rooms'), blank=True, default=0)
    option = models.ManyToManyField(HotelOption, verbose_name=_('Hotel Options'), blank=True)
    starcount = models.IntegerField(_("Count of Stars"), choices=STAR_CHOICES, default=UNKNOWN_STAR, db_index=True)
    choice = models.IntegerField(_("Type of Hotel"), choices=HOTEL_CHOICES, default=HOTEL_HOTEL, editable=False,
                                 db_index=True)
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_('Hotel Admins'), blank=True)
    point = models.DecimalField(_("Point of hotel"), editable=False, default=0, decimal_places=1, max_digits=4,
                                db_index=True)
    best_offer = models.BooleanField(verbose_name=_("Best offer"), default=False, db_index=True)
    in_top10 = models.BooleanField(verbose_name=_("In top 10"), default=False, db_index=True)
    current_amount = models.DecimalField(verbose_name=_('Current amount'), default=0, max_digits=20, decimal_places=3,
                                         db_index=True)
    booking_terms = models.TextField(verbose_name=_("Booking terms"), blank=True)
    schema_transit = models.TextField(verbose_name=_("Schema of transit"), blank=True)
    booking_terms_en = models.TextField(verbose_name=_("Booking terms(English)"), blank=True)
    schema_transit_en = models.TextField(verbose_name=_("Schema of transit(English)"), blank=True)
    payment_method = models.ManyToManyField(PaymentMethod, verbose_name=_('Payment methods'), blank=True)
    updated_date = models.DateTimeField(_("Updated date"), null=True, blank=True)
    condition_cancellation = models.TextField(verbose_name=_("Condition cancellation"), blank=True)
    condition_cancellation_en = models.TextField(verbose_name=_("Condition cancellation(English)"), blank=True)
    paid_services = models.TextField(verbose_name=_("Paid services"), blank=True)
    paid_services_en = models.TextField(verbose_name=_("Paid services(English)"), blank=True)
    time_on = models.CharField(max_length=5, verbose_name=_('Time on'), blank=True)
    time_off = models.CharField(max_length=5, verbose_name=_('Time off'), blank=True)
    work_on_request = models.BooleanField(verbose_name=_("Work on request"), default=False, db_index=True)
    hoteltype = models.ForeignKey(HotelType, verbose_name=_('Hotel type'), null=True, blank=True, db_index=True,
                                  on_delete=models.CASCADE)
    addon_city = models.ForeignKey(City, verbose_name=_('Main city'), related_name='main_city', null=True, blank=True,
                                   db_index=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Hotel")
        verbose_name_plural = _("Hotels")
        ordering = ("name",)

    objects = Manager()

    def get_address(self):
        if get_language() == 'en':
            if self.address_en:
                return self.address_en
        return self.address

    def get_schema_transit(self):
        if get_language() == 'en':
            if self.schema_transit_en:
                return self.schema_transit_en
        return self.schema_transit

    def get_booking_terms(self):
        if get_language() == 'en':
            if self.booking_terms_en:
                return self.booking_terms_en
        return self.booking_terms

    def get_condition_cancellation(self):
        if get_language() == 'en':
            if self.condition_cancellation_en:
                return self.condition_cancellation_en
        return self.condition_cancellation

    def get_paid_services(self):
        if get_language() == 'en':
            if self.paid_services_en:
                return self.paid_services_en
        return self.paid_services

    @property
    def metadesc(self):
        r = self.description
        if get_language() == 'en' and self.description_en:
            r = self.description_en
        return r.split('. ')[0] + '.'

    def get_count_stars_hotels(self):
        qs = Hotel.objects.filter(city=self.city)
        two = qs(starcount=TWO_STAR).count()
        three = qs(starcount=THREE_STAR).count()
        four = qs(starcount=FOUR_STAR).count()
        five = qs(starcount=FIVE_STAR).count()
        return [two, three, four, five]

    def fulladdress(self):
        return "%s, %s" % (self.address, self.city.name)

    def in_city(self):
        return Hotel.objects.filter(city=self.city).count()

    def in_system(self):
        return Hotel.objects.all().count()

    def stars(self):
        if self.starcount == -10:
            return None
        elif self.starcount == -1:
            return 'apartaments'
        elif self.starcount == -2:
            return 'hostel'
        elif not self.starcount:
            return 'mini'
        else:
            return range(0, int(self.starcount))

    def all_room_options(self):
        return RoomOption.objects.filter(enabled=True, room__hotel=self).select_related().order_by('category',
                                                                                                   'position',
                                                                                                   'name').distinct()

    def get_absolute_url(self):
        return reverse('hotel_detail', kwargs={'city': self.city.slug, 'slug': self.slug})

    def get_cabinet_url(self):
        return reverse('cabinet_info', kwargs={'city': self.city.slug, 'slug': self.slug})

    def get_current_percent(self):
        try:
            return AgentPercent.objects.filter(hotel=self).filter(date__lte=now()).order_by('-date')[0].percent
        except IndexError as ierr:
            return None

    def get_percent_on_date(self, on_date):
        return AgentPercent.objects.filter(hotel=self).filter(date__lte=on_date).order_by('-date')[0].percent

    @property
    def min_current_amount(self):
        return self.amount_on_date(now())

    def amount_on_date(self, on_date):
        result = PlacePrice.objects.filter(settlement__room__hotel=self, settlement__enabled=True, date=on_date).\
            aggregate(Min('amount'))
        amount = result['amount__min']
        if amount:
            return amount
        return 0

    def save(self, *args, **kwargs):
        if not self.slug:
            if not self.pk:
                super(Hotel, self).save(*args, **kwargs)
            self.slug = self.pk
        else:
            self.slug = self.slug.strip().replace(' ', '-')
            if Hotel.objects.filter(slug=self.slug, city=self.city).exclude(pk=self.pk).count():
                self.slug = self.pk
        self.updated_date = now()
        super(Hotel, self).save(*args, **kwargs)

    def update_hotel_amount(self):
        amount = self.min_current_amount
        if amount:
            self.current_amount = amount
        else:
            self.current_amount = 0
        self.save()

    def tourism_places(self):
        places = Tourism.objects.raw(places_near_object(self, settings.TOURISM_PLACES_RADIUS, 'address_tourism'))
        all_places = []
        for p in places:
            all_places.append(p.id)
        return Tourism.objects.filter(pk__in=all_places).order_by('category')

    def complete_booking_users_id(self):
        # TODO Check status of bookings
        users_id = Booking.objects.filter(hotel=self).values_list('user', flat=True)
        return users_id

    def __str__(self):
        # noinspection PyBroadException
        try:
            return _("%(hotel)s :: %(city)s") % {'hotel': self.get_name, 'city': self.city.get_name, }
        except:
            return self.name

    def available_rooms_for_guests_in_period(self, guests, from_date, to_date):
        # Find available rooms for this guests count and for searched dates
        need_days = (to_date - from_date).days
        date_period = (from_date, to_date - timedelta(days=1))
        rooms_with_amount = SettlementVariant.objects.filter(enabled=True, settlement__gte=guests,
            room__hotel=self, placeprice__date__range=date_period, placeprice__amount__gt=0).\
            annotate(num_days=Count('pk')).\
            filter(num_days__gte=need_days).order_by('room__pk').values_list('room__pk', flat=True).distinct()
        room_not_avail = Room.objects.filter(pk__in=rooms_with_amount,
            availability__date__range=date_period, availability__min_days__gt=need_days).\
            annotate(num_days=Count('pk')).filter(num_days__gt=0).order_by('pk').\
            values_list('pk', flat=True).distinct()
        rooms = Room.objects.exclude(pk__in=room_not_avail).filter(pk__in=rooms_with_amount,
            availability__date__range=date_period, availability__placecount__gt=0).\
            annotate(num_days=Count('pk')).filter(num_days__gte=need_days)
        return rooms


class RoomOptionCategory(AbstractName):
    class Meta:
        verbose_name = _("Room Option Category")
        verbose_name_plural = _("Room Option Categories")


class RoomOption(AbstractName):
    category = models.ForeignKey(RoomOptionCategory, verbose_name=_("Category"), on_delete=models.CASCADE)
    in_search = models.BooleanField(verbose_name=_("In search form?"), default=False, db_index=True)

    class Meta:
        ordering = ['position', 'name']
        verbose_name = _("Room Option")
        verbose_name_plural = _("Room Options")

    def __str__(self):
        if self.category:
            return _("%(name)s :: %(category)s") % {'name': self.name, 'category': self.category.name}
        else:
            return _("%(name)s") % {'name': self.name}


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


class Room(AbstractName):
    option = models.ManyToManyField(RoomOption, verbose_name=_('Availability options'), blank=True)
    hotel = models.ForeignKey(Hotel, verbose_name=_('Hotel'), null=True, blank=True, on_delete=models.CASCADE)
    places = models.IntegerField(_("Place Count"), choices=PLACES_CHOICES, default=PLACES_UNKNOWN, db_index=True)
    typefood = models.IntegerField(_("Type of food"), choices=TYPEFOOD, default=TYPEFOOD_RO, db_index=True)
    surface_area = models.PositiveSmallIntegerField(verbose_name=_('Surface area (m2)'), default=0, db_index=True)

    class Meta:
        verbose_name = _("Room")
        verbose_name_plural = _("Rooms")

    objects = Manager()

    def __str__(self):
        try:
            return _("%(room)s :: %(places)s :: %(hotel)s") % {'room': self.get_name, 'places': self.places,
                                                               'hotel': self.hotel.get_name}
        except:
            return self.name

    @property
    def metadesc(self):
        r = self.description
        if get_language() == 'en' and self.description_en:
            r = self.description_en
        return r.split('. ')[0] + '.'

    @property
    def min_current_amount(self):
        return self.amount_on_date(now())

    def amount_on_date(self, on_date, guests=None):
        result = PlacePrice.objects.filter(settlement__room=self, settlement__enabled=True, date=on_date).\
            aggregate(Min('amount'))
        amount = result['amount__min']
        if amount:
            return amount
        return 0

    def amount_date_guests(self, on_date, guests):
        # noinspection PyBroadException
        try:
            s = SettlementVariant.objects.select_related().filter(room=self, enabled=True, settlement__gte=guests).\
                order_by('settlement')[0]
            return s.amount_on_date(on_date)
        except:
            return None

    def discount_on_date(self, on_date):
        # noinspection PyBroadException
        try:
            return Discount.objects.get(room=self, date=on_date).discount
        except:
            return None

    def settlement_on_date_for_guests(self, on_date, guests):
        result = SettlementVariant.objects.filter(room=self, enabled=True, settlement__gte=guests).\
            aggregate(Min('settlement'))
        return result['settlement__min']

    def active_settlements(self):
        return SettlementVariant.objects.filter(room=self, enabled=True).order_by('settlement')

    def get_absolute_url(self):
        return reverse('room_detail', kwargs={'city': self.hotel.city.slug, 'slug': self.hotel.slug, 'pk': self.pk})

    def active_discounts(self):
        discounts = RoomDiscount.objects.filter(room=self, discount__enabled=True).\
            values_list('discount__pk', flat=True).distinct()
        return Discount.objects.filter(pk__in=discounts).order_by('pk')

    def inactive_discounts(self):
        discounts = RoomDiscount.objects.filter(room=self, discount__enabled=True).\
            values_list('discount__pk', flat=True).distinct()
        return Discount.objects.filter(hotel=self.hotel).exclude(pk__in=discounts).order_by('pk')

    @property
    def simple_discount(self):
        result, created = SimpleDiscount.objects.get_or_create(room=self)
        return result


class SettlementVariant(models.Model):
    room = models.ForeignKey(Room, verbose_name=_('Room'), on_delete=models.CASCADE)
    settlement = models.PositiveSmallIntegerField(_("Settlement"), db_index=True)
    enabled = models.BooleanField(verbose_name=_('Enabled'), default=True, db_index=True)

    class Meta:
        verbose_name = _("Settlement Variant")
        verbose_name_plural = _("Settlements Variants")

    def __str__(self):
        try:
            return _("Settlement -> %(settlement)s in %(room)s :: %(places)s :: %(hotel)s") % {
                'settlement': self.settlement, 'room': self.room.get_name, 'places': self.room.places,
                'hotel': self.room.hotel.get_name}
        except:
            return "Settlement for hotel %s" % self.room.hotel.get_name

    def current_amount(self):
        result = PlacePrice.objects.filter(settlement=self, date__lte=now()).order_by('-date')
        if result:
            return result[0].amount
        else:
            return 0

    def amount_on_date(self, on_date):
        result = PlacePrice.objects.filter(settlement=self, date__lte=on_date).order_by('-date')
        if result:
            return result[0].amount
        else:
            return 0

    @property
    def min_current_amount(self):
        return self.current_amount()


STATUS_UNKNOWN = 0
STATUS_ACCEPTED = 1
STATUS_CONFIRMED = 2
STATUS_CANCELED_CLIENT = 3
STATUS_CANCELED_HOTEL = 4
STATUS_NOT_ARRIVED = 5
STATUS_COMPLETED = 6

STATUS_CHOICES = (
    (STATUS_UNKNOWN, _("Unknown")),
    (STATUS_ACCEPTED, _("Accepted")),
    (STATUS_CONFIRMED, _("Confirmed")),
    (STATUS_CANCELED_CLIENT, _("Canceled by client")),
    (STATUS_CANCELED_HOTEL, _("Canceled by hotel")),
    (STATUS_NOT_ARRIVED, _("Not arrived")),
    (STATUS_COMPLETED, _("Completed")),
)

BOOKING_UNKNOWN = 0
BOOKING_UB = 1
BOOKING_GB = 2
BOOKING_NR = 3

BOOKING_CHOICES = (
    (BOOKING_UNKNOWN, _("Unknown")),
    (BOOKING_UB, _("Unguaranteed booking")),
    (BOOKING_GB, _("Guaranteed booking")),
    (BOOKING_NR, _("Non-return rate")),
)


class Booking(MoneyBase, AbstractIP):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), blank=True, null=True, on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name=_("Creation date"), default=now)
    system_id = models.IntegerField(_("ID in system"), default=0)
    from_date = models.DateField(_("From"))
    to_date = models.DateField(_("To"))
    settlement = models.ForeignKey(SettlementVariant, verbose_name=_('Settlement Variant'), null=True,
                                   on_delete=models.SET_NULL)
    settlement_txt = models.CharField(verbose_name=_("Settlement Variant in text"), max_length=255, blank=True)
    hotel = models.ForeignKey(Hotel, verbose_name=_('Hotel'), blank=True, null=True, on_delete=models.SET_NULL)
    hotel_txt = models.CharField(verbose_name=_("Hotel in text"), max_length=255, blank=True)
    status = models.IntegerField(_("Booking status"), choices=STATUS_CHOICES, default=STATUS_UNKNOWN)
    first_name = models.CharField(verbose_name=_("First name"), max_length=100)
    middle_name = models.CharField(verbose_name=_("Middle name"), max_length=100, blank=True)
    last_name = models.CharField(verbose_name=_("Last name"), max_length=100)
    phone = models.CharField(max_length=100, verbose_name=_('Phone'), blank=True)
    email = models.CharField(_('E-mail'), blank=True, max_length=100)
    uuid = models.CharField(verbose_name=_("Unique ID"), max_length=64, blank=True, editable=False)
    commission = models.DecimalField(verbose_name=_('Commission'), default=0, max_digits=20, decimal_places=3)
    hotel_sum = models.DecimalField(verbose_name=_('Hotel Sum'), default=0, max_digits=20, decimal_places=3)
    card_number = models.CharField(verbose_name=_("Card number"), max_length=16, blank=True)
    card_valid = models.CharField(verbose_name=_("Card valid to"), max_length=5, blank=True)
    card_holder = models.CharField(verbose_name=_("Card holder"), max_length=50, blank=True)
    card_cvv2 = models.CharField(verbose_name=_("Card verification value(CVV2)"), max_length=4, blank=True)
    payment_method = models.ForeignKey(PaymentMethod, verbose_name=_('Payment method'), null=True, on_delete=models.CASCADE)
    enabled = models.BooleanField(verbose_name=_('Enabled'), default=False, db_index=True)
    guests = models.PositiveSmallIntegerField(_("Guests"), db_index=True, default=0)
    btype = models.IntegerField(_("Booking type"), choices=BOOKING_CHOICES, default=BOOKING_UNKNOWN)
    bdiscount = models.PositiveSmallIntegerField(verbose_name=_('Discount percent'), default=0, db_index=True)
    typefood = models.IntegerField(_("Type of food"), choices=TYPEFOOD, db_index=True, null=True)
    freecancel = models.PositiveSmallIntegerField(verbose_name=_('Free cancel days'), default=0, db_index=True)
    penaltycancel = models.DecimalField(verbose_name=_('Penalty for cancellation'), default=0, max_digits=20,
                                        decimal_places=3)
    comment = models.TextField(verbose_name=_("Client comment"), blank=True, default='')
    amount_no_discount = models.DecimalField(verbose_name=_('Amount without discount'), default=0, max_digits=22,
                                             decimal_places=5, db_index=True)
    cancel_time = models.DateTimeField(verbose_name=_("Time/date of cancellation"), blank=True, null=True)

    objects = Manager()

    class Meta:
        ordering = ("-date",)
        verbose_name = _("Booking")
        verbose_name_plural = _("Bookings")

    def __str__(self):
        return "Booking - %s" % self.pk

    @property
    def days(self):
        return (self.to_date - self.from_date).days

    @property
    def freecancel_before(self):
        if self.freecancel > 0:
            return self.from_date - timedelta(days=self.freecancel)
        return False

    @property
    def allow_penalty(self):
        if self.freecancel_before and self.hotel and self.btype == BOOKING_GB:
            offset = self.hotel.city.time_offset
            for_time = self.hotel.time_on
            for_time1 = time(int(for_time[:2]), int(for_time[3:5]))
            if now() > datetime.combine(self.freecancel_before, for_time1) - timedelta(hours=offset):
                return True
        return False

    def get_absolute_url(self):
        if not self.uuid:
            self.save()
        return reverse('booking_hotel_detail', kwargs={'slug': self.uuid})

    def get_client_url(self):
        if not self.uuid:
            self.save()
        return reverse('booking_user_detail', kwargs={'slug': self.uuid})

    @property
    def room_day_cost(self):
        return self.amount / self.days

    @property
    def room_day_cost_no_amount(self):
        if self.amount_no_discount > 0:
            return self.amount_no_discount / self.days
        if self.bdiscount > 0:
            return ((self.amount * 100) / (100 - self.bdiscount)) / self.days
        return self.room_day_cost

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid4()
        if self.system_id < 1:
            new_id = random.randint(100000000, 999999999)
            while Booking.objects.filter(system_id=new_id).count() > 0:
                new_id = random.randint(100000000, 999999999)
            self.system_id = new_id
        super(Booking, self).save(*args, **kwargs)


class AgentPercent(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    date = models.DateField(verbose_name=_("From date"), db_index=True)
    percent = models.DecimalField(verbose_name=_('Percent'), blank=True, decimal_places=1, max_digits=4, default=0,
                                  db_index=True)

    class Meta:
        verbose_name = _("Agent Percent")
        verbose_name_plural = _("Agent Percents")
        ordering = ("hotel",)

    objects = Manager()

    def __str__(self):
        return _("For %(hotel)s on date %(date)s percent is %(percent)s") % dict(hotel=self.hotel.name, date=self.date,
                                                                                 percent=self.percent)


class Review(AbstractIP, HotelPoints):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name=_("Published by"), default=now, db_index=True)
    review = models.TextField(verbose_name=_("Review"), blank=True)
    username = models.CharField(verbose_name=_("Guest username"), max_length=100)
    booking = models.ForeignKey(Booking, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-date', ]
        verbose_name = _("Client review")
        verbose_name_plural = _("Client reviews")

    def __str__(self):
        return _("Review client %(client)s for hotel %(hotel)s is -> %(review)s") % dict(
            client=self.user.get_full_name(), hotel=self.hotel.name, review=self.review)


class Availability(models.Model):
    room = models.ForeignKey(Room, verbose_name=_('Room'), null=True, blank=True, on_delete=models.CASCADE)
    date = models.DateField(verbose_name=_("On date"), db_index=True)
    placecount = models.IntegerField(verbose_name=_('Count of places'), default=0, db_index=True)
    min_days = models.IntegerField(verbose_name=_('Minimum days'), blank=True, null=True, db_index=True)

    class Meta:
        verbose_name = _("Availability Place")
        verbose_name_plural = _("Availabilities Places")

    def __str__(self):
        return _("Availability place %(place)s for hotel %(hotel)s on date %(date)s is -> %(count)s") % dict(
            place=self.room.name, hotel=self.room.hotel.name, date=self.date, count=self.placecount)


DISCOUNT_UNKNOWN = 0
DISCOUNT_NOREFUND = 1
DISCOUNT_EARLY = 2
DISCOUNT_LATER = 3
DISCOUNT_PERIOD = 4
DISCOUNT_PACKAGE = 5
DISCOUNT_HOLIDAY = 6
DISCOUNT_SPECIAL = 7
DISCOUNT_LAST_MINUTE = 8
DISCOUNT_CREDITCARD = 9
DISCOUNT_NORMAL = 10


DISCOUNT_CHOICES = (
    (DISCOUNT_UNKNOWN, _("No discount")),
    (DISCOUNT_NOREFUND, _("Non-return rate")),
    (DISCOUNT_EARLY, _("Early booking")),
    (DISCOUNT_LATER, _("Later booking")),
    (DISCOUNT_PERIOD, _("Booking on nights count")),
    (DISCOUNT_PACKAGE, _("Package discount")),
    (DISCOUNT_HOLIDAY, _("Holidays discount")),
    (DISCOUNT_SPECIAL, _("Special discount")),
    (DISCOUNT_LAST_MINUTE, _("Last minute discount")),
    (DISCOUNT_CREDITCARD, _("Creditcard booking discount")),
    (DISCOUNT_NORMAL, _("Normal discount")),
)


class Discount(AbstractName, AbstractDate):
    hotel = models.ForeignKey(Hotel, verbose_name=_('Hotel'), on_delete=models.CASCADE)
    choice = models.IntegerField(verbose_name=_("Type of discount"), choices=DISCOUNT_CHOICES, default=DISCOUNT_UNKNOWN,
                                 db_index=True)
    days = models.SmallIntegerField(verbose_name=_("Count of days"), blank=True, null=True)
    at_price_days = models.SmallIntegerField(verbose_name=_("At price of days"), blank=True, null=True)
    time_on = models.TimeField(verbose_name=_('Time on'), blank=True, null=True)
    time_off = models.TimeField(verbose_name=_('Time off'), blank=True, null=True)
    percentage = models.BooleanField(verbose_name=_('Percentage discount'), default=True, db_index=True)
    apply_norefund = models.BooleanField(verbose_name=_('Apply norefund discount'), default=False, db_index=True)
    apply_creditcard = models.BooleanField(verbose_name=_('Apply creditcard discount'), default=False, db_index=True)
    apply_package = models.BooleanField(verbose_name=_('Apply package discount'), default=False, db_index=True)
    apply_period = models.BooleanField(verbose_name=_('Apply period discount'), default=False, db_index=True)

    class Meta:
        ordering = ['-pk', ]
        verbose_name = _("Discount")
        verbose_name_plural = _("Discounts")

    def __str__(self):
        return _("Discount hotel %(hotel)s -> %(discount)s") % dict(hotel=self.hotel.name,
                                                                    discount=self.get_choice_display())

    @property
    def quantities(self):
        if self.percentage:
            return _('(in percents)')
        else:
            return _('(to the amount)')

    @property
    def algorithm(self):
        if self.choice == DISCOUNT_NOREFUND:
            return format_lazy('{} {}', _('No refund tariff'), self.quantities)
        elif self.choice == DISCOUNT_EARLY:
            return format_lazy('{} {}', _('Booking, earlier than %s day(days) before arrival') % self.days, self.quantities)
        elif self.choice == DISCOUNT_LATER:
            return format_lazy('{} {}', _('Booking, later than %s day(days) before arrival') % self.days, self.quantities)
        elif self.choice == DISCOUNT_PERIOD:
            return format_lazy('{} {}', _('Booking at least %s day(days)') % self.days, self.quantities)
        elif self.choice == DISCOUNT_PACKAGE:
            return _('Package: booking %(days)s day(days) at price of %(price_days)s day(days)') % \
                dict(days=self.days, price_days=self.at_price_days)
        elif self.choice == DISCOUNT_HOLIDAY:
            return format_lazy('{} {}', _('Booking in holidays/weekend'), self.quantities)
        elif self.choice == DISCOUNT_SPECIAL:
            return format_lazy('{} {}', _('Special discount'), self.quantities)
        elif self.choice == DISCOUNT_LAST_MINUTE:
            return format_lazy('{} {}', _('Booking after standard arrival time, over the time %(time_from)s - %(time_to)s')
                                 % dict(time_from=date(self.time_on, 'H:i'), time_to=date(self.time_off, 'H:i')),
                                 self.quantities)
        elif self.choice == DISCOUNT_CREDITCARD:
            return format_lazy('{} {}', _('Booking with creditcard'), self.quantities)
        elif self.choice == DISCOUNT_NORMAL:
            return format_lazy('{} {}', _('Simple discount'), self.quantities)
        else:
            return None


class RoomDiscount(models.Model):
    date = models.DateField(verbose_name=_("On date"), db_index=True)
    discount = models.ForeignKey(Discount, verbose_name=_("Discount of hotel's"), on_delete=models.CASCADE)
    room = models.ForeignKey(Room, verbose_name=_("Room of hotel's"), on_delete=models.CASCADE)
    value = models.DecimalField(verbose_name=_('Value of discount'), default=0, max_digits=20, decimal_places=3,
                                db_index=True)

    class Meta:
        ordering = ['-pk', ]
        verbose_name = _("Room discount")
        verbose_name_plural = _("Room discounts")

    def __str__(self):
        return _('Discount on %(date)s - %(val)s') % dict(date=self.date, val=self.value)


class SimpleDiscount(models.Model):
    room = models.ForeignKey(Room, verbose_name=_("Room of hotel's"), on_delete=models.CASCADE)
    ub = models.BooleanField(verbose_name=_('Unguaranteed booking enabled'), default=False, db_index=True)
    ub_discount = models.PositiveSmallIntegerField(verbose_name=_('Discount ub'), default=0, db_index=True)
    gb = models.BooleanField(verbose_name=_('Guaranteed booking enabled'), default=False, db_index=True)
    gb_days = models.PositiveSmallIntegerField(verbose_name=_('Free cancel gb days'), default=0, db_index=True)
    gb_penalty = models.PositiveSmallIntegerField(verbose_name=_('Penalty for gb cancel'), default=0, db_index=True)
    gb_discount = models.PositiveSmallIntegerField(verbose_name=_('Discount gb'), default=0, db_index=True)
    nr = models.BooleanField(verbose_name=_('Non-return rate enabled'), default=False, db_index=True)
    nr_discount = models.PositiveSmallIntegerField(verbose_name=_('Discount nr'), default=0, db_index=True)

    class Meta:
        ordering = ['-pk', ]
        verbose_name = _("Simple room discount")
        verbose_name_plural = _("Simple room discounts")

    def __str__(self):
        return _('Discount for room %(room)s in %(hotel)s') % dict(room=self.room.name, hotel=self.room.hotel.name)


class PlacePrice(MoneyBase):
    date = models.DateField(verbose_name=_("On date"), db_index=True)
    settlement = models.ForeignKey(SettlementVariant, verbose_name=_('Settlement Variant'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Place Price")
        verbose_name_plural = _("Places Prices")

    def __str__(self):
        return _(
            "Price settlement %(settlement)s for hotel %(hotel)s on date %(date)s is -> %(price)s %(currency)s") % dict(
                settlement=self.settlement.settlement, hotel=self.settlement.room.hotel.name, date=self.date,
                price=self.amount, currency=self.currency.code)

    def save(self, *args, **kwargs):
        cache.delete('hotel_prices')
        super(PlacePrice, self).save(*args, **kwargs)


class RequestAddHotel(AbstractIP):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), blank=True,
                             null=True, on_delete=models.CASCADE)
    register_date = models.DateTimeField(_("Register date"), default=now)
    city = models.CharField(verbose_name=_("City"), max_length=100, blank=True)
    address = models.CharField(verbose_name=_("Address"), max_length=100, blank=True)
    name = models.CharField(verbose_name=_("Name"), max_length=100, blank=True)
    email = models.CharField(verbose_name=_("Email"), max_length=100, blank=True)
    phone = models.CharField(verbose_name=_("Phone"), max_length=100, blank=True)
    fax = models.CharField(verbose_name=_("Fax"), max_length=100, blank=True)
    contact_email = models.CharField(verbose_name=_("Contact email"), max_length=100, blank=True)
    website = models.CharField(verbose_name=_("Website"), max_length=100, blank=True)
    rooms_count = models.CharField(verbose_name=_("Count of rooms"), max_length=100, blank=True)
    starcount = models.IntegerField(_("Count of Stars"), choices=STAR_CHOICES, default=UNKNOWN_STAR)

    class Meta:
        verbose_name = _("Request for add hotel")
        verbose_name_plural = _("Requests for add hotels")
        ordering = ("-pk",)


def update_hotel_point(sender, instance, **kwargs):
    # noinspection PyBroadException
    try:
        hotel = instance.hotel
        all_points = Review.objects.filter(hotel=hotel).aggregate(Avg('food'), Avg('service'),
                                                                  Avg('purity'), Avg('transport'), Avg('prices'))
        hotel.food = Decimal(str(all_points['food__avg'])).quantize(Decimal('1.0'))
        hotel.service = Decimal(str(all_points['service__avg'])).quantize(Decimal('1.0'))
        hotel.purity = Decimal(str(all_points['purity__avg'])).quantize(Decimal('1.0'))
        hotel.transport = Decimal(str(all_points['transport__avg'])).quantize(Decimal('1.0'))
        hotel.prices = Decimal(str(all_points['prices__avg'])).quantize(Decimal('1.0'))
        h_point = (hotel.food + hotel.service + hotel.purity + hotel.transport + hotel.prices) / 5
        hotel.point = h_point
        hotel.save()
    except:
        pass


signals.post_save.connect(update_hotel_point, sender=Review, dispatch_uid="nnmware_id")
signals.post_delete.connect(update_hotel_point, sender=Review, dispatch_uid="nnmware_id")


class HotelSearch(AbstractIP):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), blank=True,
                             null=True, on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name=_("Creation date"), default=now, db_index=True)
    city = models.CharField(verbose_name=_("City"), max_length=100, blank=True)
    hotel = models.CharField(verbose_name=_("Hotel"), max_length=100, blank=True)
    from_date = models.DateField(_("From"))
    to_date = models.DateField(_("To"))
    guests = models.PositiveSmallIntegerField(_("Guests"), db_index=True, default=0)

    class Meta:
        verbose_name = _("Search parameters")
        verbose_name_plural = _("Searched parameters")
        ordering = ("-pk",)

    def __str__(self):
        return _('IP %(ip)s - %(date)s') % dict(ip=self.ip, date=self.date)
