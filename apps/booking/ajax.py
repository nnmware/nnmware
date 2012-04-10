from datetime import datetime
from django.conf import settings
from django.http import HttpResponse
from django.utils import simplejson
from nnmware.apps.booking.models import SettlementVariant, PlacePrice, Room, Availability
from nnmware.apps.money.models import Currency
from nnmware.core.http import LazyEncoder
import time

def room_rate(request):
    currency = Currency.objects.get(code=settings.DEFAULT_CURRENCY)
    try:
        value = request.REQUEST['value']
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
        settlements = SettlementVariant.objects.filter(room=room).order_by('settlement')
        results = []
        for s in settlements:
            results.append(s.settlement)
        payload = {'success': True, 'settlements':results}
    except :
        payload = {'success': False}
    return HttpResponse(simplejson.dumps(payload, cls=LazyEncoder), content_type='application/json')
