from datetime import datetime, timedelta
from django.conf import settings
from django.http import HttpResponse
from django.utils import simplejson
from nnmware.apps.booking.models import SettlementVariant, PlacePrice, Room, Availability
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
    if 1>0:
        room_id = request.REQUEST['room_id']
        s = request.REQUEST['settlements']
        from_date = convert_to_date(request.REQUEST['from_date'])
        to_date = convert_to_date(request.REQUEST['to_date'])
        room = Room.objects.get(id=room_id)
        settlement = SettlementVariant.objects.filter(room=room, settlement=s)
        results = []
        delta = to_date-from_date
        all_amount = 0
        on_date = from_date
        while on_date < to_date:
            price = PlacePrice.objects.get(settlement=settlement, date = on_date)
            all_amount +=int(price.amount)
            on_date = on_date+timedelta(days=1)
        all_amount = str(all_amount)+price.currency.code
        payload = {'success': True, 'dayscount':delta.days, 'amount':all_amount}
#    except :
#        payload = {'success': False}
    return HttpResponse(simplejson.dumps(payload, cls=LazyEncoder), content_type='application/json')








