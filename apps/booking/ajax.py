# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from decimal import Decimal
from exceptions import ValueError, Exception
import json
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.db.models.aggregates import Avg
from django.http import HttpResponse, Http404
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.address.models import City
from nnmware.apps.booking.models import SettlementVariant, PlacePrice, Room, Availability, Hotel, RequestAddHotel, \
    Review, Booking, PaymentMethod, Discount
from nnmware.apps.money.models import Currency
import time
from nnmware.core.http import get_session_from_request, LazyEncoder
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


def filter_hotels_on_map(request, hotels):
    try:
        searched = hotels
        f_date = request.REQUEST.get('start_date') or None
        amount_min = request.REQUEST.get('amount_min') or None
        amount_max = request.REQUEST.get('amount_max') or None
        options = request.REQUEST.getlist('options') or None
        stars = request.REQUEST.getlist('stars') or None
        if amount_max and amount_min:
            if f_date:
                from_date = convert_to_date(f_date)
                hotels_with_amount = PlacePrice.objects.filter(date=from_date,
                    amount__range=(amount_min, amount_max)).values_list('settlement__room__hotel__pk',
                    flat=True).distinct()
            else:
                hotels_with_amount = PlacePrice.objects.filter(date=datetime.today(),
                    amount__range=(amount_min, amount_max)).values_list('settlement__room__hotel__pk',
                    flat=True).distinct()
            searched = searched.filter(pk__in=hotels_with_amount, work_on_request=False)
        if options:
            for option in options:
                searched = searched.filter(option=option)
        if stars:
            searched = searched.filter(starcount__in=stars)
        searched = searched.order_by('starcount')
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


def hotels_in_city(request):
    try:
        c = request.REQUEST['city']
        path = request.REQUEST['path'] or None
        if path:
            key = sha1('%s' % (path,)).hexdigest()
            data_key = cache.get(key)
            searched = Hotel.objects.filter(pk__in=data_key)
        else:
            city = City.objects.get(pk=c)
            searched = Hotel.objects.filter(city=city)
        return filter_hotels_on_map(request, searched)
    except:
        payload = {'success': False}
    return AjaxLazyAnswer(payload)


def hotels_in_country(request):
    try:
        searched = Hotel.objects.all()
        return filter_hotels_on_map(request, searched)
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


def booking_sysadm(request, pk, action):
    if not request.is_ajax():
        raise Http404
    try:
        if not request.user.is_superuser:
            raise UserNotAllowed
        booking = Booking.objects.select_related().get(id=pk)
        if action == 'delete':
            from_date = booking.from_date
            to_date = booking.to_date
            settlement = booking.settlement
            while from_date < to_date:
                avail = Availability.objects.get(room=settlement.room, date=from_date)
                avail.placecount += 1
                avail.save()
            booking.delete()
            url = reverse_lazy('bookings_list')
        elif action == 'enable':
            booking.enabled = True
            booking.save()
            url = reverse_lazy('booking_admin_detail', args=[booking.uuid, ])
        else:
            raise UserNotAllowed
        payload = {'success': True, 'location': url}
    except UserNotAllowed:
        payload = {'success': False, 'error_msg': _('You are not allowed for this action.')}
    except:
        payload = {'success': False}
    return AjaxLazyAnswer(payload)
