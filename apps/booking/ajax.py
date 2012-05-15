# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Avg
from nnmware.apps.address.models import City
from nnmware.apps.booking.models import SettlementVariant, PlacePrice, Room, Availability, Hotel, RequestAddHotel, Review, Booking
from nnmware.apps.money.models import Currency
import time
from nnmware.core.utils import convert_to_date
from nnmware.core.ajax import AjaxLazyAnswer

class UserNotAllowed(Exception):
    pass

def room_rate(request):
    try:
        room = Room.objects.get(id=request.REQUEST['room_id'])
        if request.user not in room.hotel.admins.all() and not request.user.is_superuser:
            raise UserNotAllowed
        currency = Currency.objects.get(code=settings.DEFAULT_CURRENCY)
        value = int(request.REQUEST['value'])
        on_date = request.REQUEST['on_date'][1:]
        on_date = datetime.fromtimestamp(time.mktime(time.strptime(on_date, "%d%m%Y")))
        row_id = request.REQUEST['row']
        if row_id == 'placecount':
            try:
                availability = Availability.objects.get(date=on_date, room=room)
            except :
                availability = Availability(date=on_date, room=room)
            availability.placecount = value
            availability.save()
        else:
            settlement_id = int(row_id[1:])
            settlement = SettlementVariant.objects.get(id=settlement_id)
            try:
                placeprice = PlacePrice.objects.get(date=on_date,settlement=settlement)
            except :
                placeprice = PlacePrice(date=on_date,settlement=settlement)
            placeprice.amount = value
            placeprice.currency = currency
            placeprice.save()
        payload = {'success': True}
    except UserNotAllowed:
        payload = {'success': False, 'error_msg':_('You are not allowed change room rates.')}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def room_variants(request):
    try:
        room = Room.objects.get(id=request.REQUEST['room_id'])
        if request.user not in room.hotel.admins.all() and not request.user.is_superuser:
            raise UserNotAllowed
        settlements = SettlementVariant.objects.filter(room=room,enabled=True).order_by('settlement')
        results = []
        for s in settlements:
            results.append(s.settlement)
        payload = {'success': True, 'settlements':results}
    except UserNotAllowed:
        payload = {'success': False, 'error_msg':_('You are not allowed change room variants.')}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def room_delete(request, pk):
    try:
        room = Room.objects.get(id=pk)
        if request.user not in room.hotel.admins.all() and not request.user.is_superuser:
            raise UserNotAllowed
        room.delete()
        payload = {'success': True}
    except UserNotAllowed:
        payload = {'success': False, 'error_msg':_('You are not allowed change room variants.')}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def get_booking_amount(request):
    try:
        room_id = request.REQUEST['room_id']
        s = request.REQUEST['settlements']
        from_date = convert_to_date(request.REQUEST['from_date'])
        to_date = convert_to_date(request.REQUEST['to_date'])
        room = Room.objects.get(id=room_id)
        settlement = SettlementVariant.objects.filter(room=room, settlement=s)
        delta = to_date-from_date
        all_amount = 0
        on_date = from_date
        while on_date < to_date:
            price = PlacePrice.objects.get(settlement=settlement, date = on_date)
            all_amount +=int(price.amount)
            on_date = on_date+timedelta(days=1)
        all_amount = str(all_amount)+price.currency.code
        payload = {'success': True, 'dayscount':delta.days, 'amount':all_amount}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def hotel_add(request):
    try:
        if not request.user.is_superuser:
            raise UserNotAllowed
        request_id = request.REQUEST['request_id']
        name = request.REQUEST['name']
        c = request.REQUEST['city']
        address = request.REQUEST['address']
        email = request.REQUEST['email']
        phone = request.REQUEST['phone']
        fax = request.REQUEST['fax']
        contact_email = request.REQUEST['contact_email']
        website = request.REQUEST['website']
        rooms_count = request.REQUEST['rooms_count']
        starcount = request.REQUEST['starcount']
        try:
            city = City.objects.get(name=c)
        except ObjectDoesNotExist:
            city = City()
            city.name = c
            city.save()
        hotel = Hotel()
        hotel.name = name
        hotel.city = city
        hotel.address = address
        hotel.email = email
        hotel.phone = phone
        hotel.fax = fax
        hotel.contact_email = contact_email
        hotel.website = website
        hotel.room_count = rooms_count
        hotel.starcount = starcount
        hotel.save()
        location = reverse('cabinet_info', args=[hotel.pk])
        RequestAddHotel.objects.get(id=request_id).delete()
        payload = {'success': True, 'location':location}
    except UserNotAllowed:
        payload = {'success': False, 'error_msg':_('You are not allowed add hotel.')}
    return AjaxLazyAnswer(payload)

def client_review(request, pk):
    try:
        hotel = Hotel.objects.get(id=pk)
        guests = Booking.objects.filter(hotel=hotel,to_date__gte=datetime.now()).values_list('user', flat=True)
        if request.user.pk not in guests or not request.user.is_authenticated():
            raise UserNotAllowed
        if Review.objects.filter(hotel=hotel,user=request.user).count():
            raise UserNotAllowed
        food = request.REQUEST['point_food']
        service = request.REQUEST['point_service']
        purity = request.REQUEST['point_purity']
        transport = request.REQUEST['point_transport']
        prices = request.REQUEST['point_prices']
        review = request.REQUEST['review']
        r = Review()
        r.user = request.user
        r.hotel = hotel
        r.food = food
        r.service = service
        r.purity = purity
        r.transport = transport
        r.prices = prices
        r.review = review
        r.save()
        payload = {'success': True}
    except UserNotAllowed:
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def tourism_places(request):
    try:
        h = request.REQUEST['hotel']
        hotel = Hotel.objects.get(pk=h)
        results = []
        for tourism in hotel.tourism_places().order_by('category'):
            if tourism.category.icon:
                icon = tourism.category.icon.url
            else:
                icon = ''
            answer = {'name':tourism.get_name, 'latitude':tourism.latitude,
                      'category':tourism.category.name,'category_id':tourism.category.pk,
                      'longitude':tourism.longitude,'icon':icon }
            results.append(answer)
        payload = {'success': True, 'tourism':results}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def hotels_in_city(request):
    try:
        c = request.REQUEST['city']
        city = City.objects.get(pk=c)
        results = []
        for hotel in Hotel.objects.filter(city=city).order_by('starcount'):
            answer = {'name':hotel.get_name, 'latitude':hotel.latitude,
                      'address':hotel.address,'id':hotel.pk,'starcount':hotel.starcount,
                      'longitude':hotel.longitude, 'starcount_name':hotel.get_starcount_display()}
            results.append(answer)
        payload = {'success': True, 'hotels':results}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)
