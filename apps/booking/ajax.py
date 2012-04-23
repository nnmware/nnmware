from datetime import datetime, timedelta
from decimal import Decimal
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Avg
from django.http import HttpResponse
from django.utils import simplejson
from nnmware.apps.address.models import City
from nnmware.apps.booking.models import SettlementVariant, PlacePrice, Room, Availability, Hotel, RequestAddHotel, Review
from nnmware.apps.money.models import Currency
from nnmware.core.http import LazyEncoder
import time
from nnmware.core.utils import convert_to_date

def room_rate(request):
    currency = Currency.objects.get(code=settings.DEFAULT_CURRENCY)
    try:
        value = int(request.REQUEST['value'])
        on_date = request.REQUEST['on_date'][1:]
        on_date = datetime.fromtimestamp(time.mktime(time.strptime(on_date, "%d%m%Y")))
        row_id = request.REQUEST['row']
        room_id = request.REQUEST['room_id']
        if row_id == 'placecount':
            room = Room.objects.get(id=room_id)
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
    except :
        payload = {'success': False}
    return HttpResponse(simplejson.dumps(payload, cls=LazyEncoder), content_type='application/json')

def room_variants(request):
    try:
        room_id = request.REQUEST['room_id']
        room = Room.objects.get(id=room_id)
        settlements = SettlementVariant.objects.filter(room=room,enabled=True).order_by('settlement')
        results = []
        for s in settlements:
            results.append(s.settlement)
        payload = {'success': True, 'settlements':results}
    except :
        payload = {'success': False}
    return HttpResponse(simplejson.dumps(payload, cls=LazyEncoder), content_type='application/json')

def room_delete(request, pk):
    try:
        room = Room.objects.get(id=pk)
        room.delete()
        payload = {'success': True}
    except :
        payload = {'success': False}
    return HttpResponse(simplejson.dumps(payload, cls=LazyEncoder), content_type='application/json')

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
    return HttpResponse(simplejson.dumps(payload, cls=LazyEncoder), content_type='application/json')

def hotel_add(request):
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
    try:
        city = City.objects.get(name=c)
    except :
        city = City()
        city.name = c
        city.save()
#    city, created = City.objects.get_or_create(name=c)
#    if created:
#        city.save()
#        city.slug = city.pk
#        city.save()
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
    hotel.save()
    location = reverse('cabinet_info', args=[hotel.pk])
    RequestAddHotel.objects.get(id=request_id).delete()
    payload = {'success': True, 'location':location}
    return HttpResponse(simplejson.dumps(payload, cls=LazyEncoder), content_type='application/json')

def client_review(request, pk):
    # TODO Make cheked of user and non-doubled review
    if 1>0:
        hotel = Hotel.objects.get(id=pk)
        food = request.REQUEST['point_food']
        service = request.REQUEST['point_service']
        purity = request.REQUEST['point_purity']
        transport = request.REQUEST['point_transport']
        prices = request.REQUEST['point_prices']
        review = request.REQUEST['review']
        user = request.user
        r = Review()
        r.user = user
        r.hotel = hotel
        r.food = food
        r.service = service
        r.purity = purity
        r.transport = transport
        r.prices = prices
        r.review = review
        r.save()
        payload = {'success': True}
#    except :
#        payload = {'success': False}
    return HttpResponse(simplejson.dumps(payload, cls=LazyEncoder), content_type='application/json')

def tourism_places(request):
    try:
        h = request.REQUEST['hotel']
        hotel = Hotel.objects.get(pk=h)
        results = []
        for tourism in hotel.tourism.all():
            answer = {'name':tourism.get_name, 'latitude':tourism.latitude,
                      'longitude':tourism.longitude}
            results.append(answer)
        payload = {'success': True, 'tourism':results}
    except :
        payload = {'success': False}
    return HttpResponse(simplejson.dumps(payload, cls=LazyEncoder), content_type='application/json')




