# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from decimal import Decimal
from exceptions import ValueError, Exception
import json
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Avg
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.address.models import City
from nnmware.apps.booking.models import SettlementVariant, PlacePrice, Room, Availability, Hotel, RequestAddHotel, \
    Review, Booking, PaymentMethod, Discount
from nnmware.apps.money.models import Currency
import time
from nnmware.core.http import get_session_from_request
from nnmware.core.imgutil import make_thumbnail
from nnmware.core.templatetags.core import get_image_attach_url
from nnmware.core.utils import convert_to_date
from nnmware.core.ajax import AjaxLazyAnswer
from django.views.decorators.cache import never_cache
from hashlib import sha1
from django.core.cache import cache


class UserNotAllowed(Exception):
    pass


class RatesError(Exception):
    pass


@never_cache
def room_rates(request):
    try:
        json_data = json.loads(request.body)
        currency = Currency.objects.get(code=settings.DEFAULT_CURRENCY)
        room = Room.objects.get(id=int(json_data['room_id']))
        if request.user not in room.hotel.admins.all() and not request.user.is_superuser:
            raise UserNotAllowed
            # find settlements keys in data
        all_settlements, discount = [], []
        for k in json_data.keys():
            if k[0] == 's':
                all_settlements.append(k)
            elif k == 'discount':
                discount.append(k)
        for i, v in enumerate(json_data['dates']):
            on_date = datetime.fromtimestamp(time.mktime(time.strptime(v, "%d%m%Y")))
            if 'placecount' in json_data.keys():
                try:
                    placecount = int(json_data['placecount'][i])
                    try:
                        min_days = int(json_data['min_days'][i])
                    except:
                        min_days = None
                        # store availability
                    availability, created = Availability.objects.get_or_create(date=on_date, room=room)
                    availability.placecount = placecount
                    if min_days is not None:
                        availability.min_days = min_days
                    availability.save()
                except ValueError:
                    pass
            for k in discount:
                try:
                    discount_on_date = int(json_data[k][i])
                    if discount_on_date < 1 or discount_on_date > 99:
                        raise ValueError
                    d, created = Discount.objects.get_or_create(date=on_date, room=room)
                    d.discount = discount_on_date
                    d.save()
                except ValueError:
                    pass
            for k in all_settlements:
                try:
                    settlement_id = int(k[1:])
                    settlement = SettlementVariant.objects.get(id=settlement_id)
                    price = int(json_data[k][i])
                    placeprice, created = PlacePrice.objects.get_or_create(date=on_date, settlement=settlement)
                    placeprice.amount = price
                    placeprice.currency = currency
                    placeprice.save()
                except ValueError:
                    pass
        payload = {'success': True}
    except UserNotAllowed:
        payload = {'success': False}
    except:
        payload = {'success': False}
    return AjaxLazyAnswer(payload)


def room_variants(request):
    try:
        room = Room.objects.get(id=request.REQUEST['room_id'])
        if request.user not in room.hotel.admins.all() and not request.user.is_superuser:
            raise UserNotAllowed
        settlements = SettlementVariant.objects.filter(room=room, enabled=True).order_by('settlement')
        results = []
        for s in settlements:
            results.append(s.settlement)
        payload = {'success': True, 'settlements': results}
    except UserNotAllowed:
        payload = {'success': False, 'error_msg': _('You are not allowed change room variants.')}
    except:
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
        payload = {'success': False, 'error_msg': _('You are not allowed change room variants.')}
    except:
        payload = {'success': False}
    return AjaxLazyAnswer(payload)


def request_hotel_delete(request, pk):
    try:
        req_hotel = RequestAddHotel.objects.get(id=pk)
        if not request.user.is_superuser:
            raise UserNotAllowed
        req_hotel.delete()
        payload = {'success': True}
    except UserNotAllowed:
        payload = {'success': False, 'error_msg': _('You are not allowed change room variants.')}
    except:
        payload = {'success': False}
    return AjaxLazyAnswer(payload)


def get_booking_amount(request):
    try:
        room_id = request.REQUEST['room_id']
        s = request.REQUEST['guests']
        from_date = convert_to_date(request.REQUEST['from'])
        to_date = convert_to_date(request.REQUEST['to'])
        room = Room.objects.get(id=room_id)
        settlement = SettlementVariant.objects.filter(room=room, settlement=s)
        delta = to_date - from_date
        all_amount = 0
        on_date = from_date
        while on_date < to_date:
            price = PlacePrice.objects.get(settlement=settlement, date=on_date)
            all_amount += int(price.amount)
            on_date = on_date + timedelta(days=1)
        all_amount = str(all_amount) + price.currency.code
        payload = {'success': True, 'dayscount': delta.days, 'amount': all_amount}
    except:
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
        except:
            city = City(name=c)
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
        location = reverse('cabinet_info', args=[hotel.city.slug, hotel.slug])
        RequestAddHotel.objects.get(id=request_id).delete()
        payload = {'success': True, 'location': location}
    except UserNotAllowed:
        payload = {'success': False, 'error_msg': _('You are not allowed add hotel.')}
    return AjaxLazyAnswer(payload)


def client_review(request, pk):
    try:
        hotel = Hotel.objects.get(id=pk)
        #        guests = Booking.objects.filter(hotel=hotel,to_date__gte=datetime.now()).values_list('user', flat=True)
        if request.user.is_superuser:
            message = _('You are superuser and may add review.')
        elif request.user.pk in hotel.complete_booking_users_id:
            message = _('Thanks for you review!')
        else:
            raise UserNotAllowed
        if Review.objects.filter(hotel=hotel, user=request.user).count():
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
        payload = {'success': True, 'message': message}
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
            answer = {'name': tourism.get_name, 'latitude': tourism.latitude,
                      'category': tourism.category.name, 'category_id': tourism.category.pk,
                      'longitude': tourism.longitude, 'icon': icon, 'id': tourism.pk}
            results.append(answer)
        payload = {'success': True, 'tourism': results}
    except:
        payload = {'success': False}
    return AjaxLazyAnswer(payload)


def hotels_in_city(request):
    path = request.REQUEST['path'] or None
    raise ImportError, str(path.replace('&amp;', '&'))
    try:
        c = request.REQUEST['city']
        path = request.REQUEST['path'] or None

        if path:
            key = sha1('%s' % (urlencode(path).replace('&amp;', '&'),)).hexdigest()
            data_key = cache.get('list_'+key)
            searched = Hotel.objects.filter(pk__in=data_key).order_by('starcount')
        else:
            city = City.objects.get(pk=c)
            searched = Hotel.objects.filter(city=city).order_by('starcount')
        # if data_key:
        #     searched = data_key
        results = []
        for hotel in searched:
            answer = {'name': hotel.get_name, 'latitude': hotel.latitude, 'url': hotel.get_absolute_url(),
                      'address': hotel.address, 'id': hotel.pk, 'starcount': hotel.starcount,
                      'img': make_thumbnail(hotel.main_image, width=113, height=75, aspect=1),
                      'longitude': hotel.longitude, 'starcount_name': hotel.get_starcount_display(),
                      'amount': str(int(hotel.current_amount))}

            results.append(answer)
        payload = {'success': True, 'hotels': results}
    except:
        payload = {'success': False}
    return AjaxLazyAnswer(payload)


def hotels_in_country(request):
    try:
        results = []
        for hotel in Hotel.objects.all().order_by('starcount'):
            answer = {'name': hotel.get_name, 'latitude': hotel.latitude, 'url': hotel.get_absolute_url(),
                      'address': hotel.address, 'id': hotel.pk, 'starcount': hotel.starcount,
                      'img': make_thumbnail(hotel.main_image, width=113, height=75, aspect=1),
                      'longitude': hotel.longitude, 'starcount_name': hotel.get_starcount_display(),
                      'amount': str(int(hotel.current_amount))}
            results.append(answer)
        payload = {'success': True, 'hotels': results}
    except:
        payload = {'success': False}
    return AjaxLazyAnswer(payload)


def payment_method(request):
    try:
        p_m = request.REQUEST['p_m']
        payment_method = PaymentMethod.objects.get(pk=p_m)
        payload = {'success': True, 'id': payment_method.pk, 'description': payment_method.description,
                   'card': payment_method.use_card}
    except:
        payload = {'success': False}
    return AjaxLazyAnswer(payload)


def add_category(request):
    try:
        hotel_pk = request.REQUEST['hotel']
        hotel = Hotel.objects.get(pk=hotel_pk)
        if request.user not in hotel.admins.all() and not request.user.is_superuser:
            raise UserNotAllowed
        category_name = request.REQUEST['category_name']
        r = Room.objects.filter(hotel=hotel, name=category_name).count()
        if r > 0:
            raise UserNotAllowed
        room = Room(hotel=hotel, name=category_name)
        room.save()
        file_path = get_image_attach_url(room)
        form_path = reverse('cabinet_room', args=[hotel.city.slug, hotel.slug, room.pk])
        payload = {'success': True, 'file_path': file_path, 'form_path': form_path}
    except UserNotAllowed:
        payload = {'success': False}
    return AjaxLazyAnswer(payload)
