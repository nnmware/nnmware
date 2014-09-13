# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from exceptions import ValueError, Exception
import json
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import transaction
from django.db.models import Q
from django.http import Http404
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from nnmware.core.exceptions import AccessError
from nnmware.apps.address.models import City
from nnmware.apps.booking.models import SettlementVariant, PlacePrice, Room, Availability, Hotel, RequestAddHotel, \
    Review, Booking, PaymentMethod, Discount, RoomDiscount, SimpleDiscount
from nnmware.apps.booking.utils import booking_delete_client_mail, booking_new_hotel_mail
from nnmware.apps.money.models import Currency
import time
from nnmware.core.imgutil import make_thumbnail
from nnmware.core.templatetags.core import get_image_attach_url
from nnmware.core.utils import convert_to_date, setting
from nnmware.core.ajax import ajax_answer_lazy
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
        currency = Currency.objects.get(code=setting('DEFAULT_CURRENCY', 'RUB'))
        hotel = Hotel.objects.get(id=int(json_data['hotel']))
        if request.user not in hotel.admins.all() and not request.user.is_superuser:
            raise UserNotAllowed
            # find settlements keys in data
        all_rooms, all_avail, all_limits = [], [], []
        for k in json_data.keys():
            if k[0] == 'r':
                all_rooms.append(k)
            elif k[0] == 'a':
                all_avail.append(k)
            elif k[0] == 'l':
                all_limits.append(k)
        for i, v in enumerate(json_data['dates']):
            on_date = datetime.fromtimestamp(time.mktime(time.strptime(v, "%d%m%Y")))
            for k in all_rooms:
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
            for k in all_avail:
                try:
                    room_id = int(k[1:])
                    room = Room.objects.get(pk=room_id)
                    placecount = int(json_data[k][i])
                    availability, created = Availability.objects.get_or_create(date=on_date, room=room)
                    availability.placecount = placecount
                    try:
                        min_days = int(json_data['l' + k[1:]][i])
                    except:
                        min_days = None
                    if min_days is not None:
                        availability.min_days = min_days
                    availability.save()
                except ValueError:
                    pass
        payload = {'success': True}
    except UserNotAllowed:
        payload = {'success': False}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


@never_cache
def room_discounts(request):
    try:
        json_data = json.loads(request.body)
        hotel = Hotel.objects.get(id=int(json_data['hotel']))
        if request.user not in hotel.admins.all() and not request.user.is_superuser:
            raise UserNotAllowed
        all_rooms = []
        for k in json_data.keys():
            if k[0:2] == 'ub':
                all_rooms.append(k[2:])
        for r in all_rooms:
            room = Room.objects.get(pk=int(r))
            # TODO Check user rights for room
            simple_discount, created = SimpleDiscount.objects.get_or_create(room=room)
            try:
                if json_data['ub' + r][0] == '1':
                    simple_discount.ub = True
                else:
                    simple_discount.ub = False
                simple_discount.ub_days = int(json_data['ub' + r][1])
                simple_discount.ub_penalty = int(json_data['ub' + r][2])
                simple_discount.ub_discount = int(json_data['ub' + r][3])
                if json_data['gb' + r][0] == '1':
                    simple_discount.gb = True
                else:
                    simple_discount.gb = False
                simple_discount.gb_days = int(json_data['gb' + r][1])
                simple_discount.gb_penalty = int(json_data['gb' + r][2])
                simple_discount.gb_discount = int(json_data['gb' + r][3])
                if json_data['nr' + r][0] == '1':
                    simple_discount.gb = True
                else:
                    simple_discount.gb = False
                simple_discount.nr_days = int(json_data['nr' + r][1])
                simple_discount.nr_penalty = int(json_data['nr' + r][2])
                simple_discount.nr_discount = int(json_data['nr' + r][3])
                simple_discount.save()
            except:
                pass
        payload = {'success': True}
    except UserNotAllowed:
        payload = {'success': False}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def room_variants(request):
    try:
        room = Room.objects.get(id=request.POST['room_id'])
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
    return ajax_answer_lazy(payload)


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
    return ajax_answer_lazy(payload)


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
    return ajax_answer_lazy(payload)


def hotel_add(request):
    try:
        if not request.user.is_superuser:
            raise UserNotAllowed
        request_id = request.POST['request_id']
        name = request.POST['name']
        c = request.POST['city']
        address = request.POST['address']
        email = request.POST['email']
        phone = request.POST['phone']
        fax = request.POST['fax']
        contact_email = request.POST['contact_email']
        website = request.POST['website']
        rooms_count = request.POST['rooms_count']
        starcount = request.POST['starcount']
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
    return ajax_answer_lazy(payload)


def client_review(request, pk):
    try:
        hotel = Hotel.objects.get(id=pk)
        #        guests = Booking.objects.filter(hotel=hotel,to_date__gte=now()).values_list('user', flat=True)
        if request.user.is_superuser:
            message = _('You are superuser and may add review.')
        elif request.user.pk in hotel.complete_booking_users_id:
            message = _('Thanks for you review!')
        else:
            raise UserNotAllowed
        if Review.objects.filter(hotel=hotel, user=request.user).count():
            raise UserNotAllowed
        food = request.POST['point_food']
        service = request.POST['point_service']
        purity = request.POST['point_purity']
        transport = request.POST['point_transport']
        prices = request.POST['point_prices']
        review = request.POST['review']
        r = Review()
        r.user = request.user
        r.username = request.user.first_name
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
    return ajax_answer_lazy(payload)


def tourism_places(request):
    try:
        h = request.POST['hotel']
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
    return ajax_answer_lazy(payload)


def filter_hotels_on_map(request, hotels):
    try:
        searched = hotels
        f_date = request.POST.get('start_date') or None
        amount_min = request.POST.get('amount_min') or None
        amount_max = request.POST.get('amount_max') or None
        options = request.POST.getlist('options') or None
        stars = request.POST.getlist('stars') or None
        if amount_max and amount_min:
            if f_date:
                from_date = convert_to_date(f_date)
                hotels_with_amount = PlacePrice.objects.filter(date=from_date,
                    amount__range=(amount_min, amount_max)).values_list('settlement__room__hotel__pk',
                    flat=True).distinct()
            else:
                hotels_with_amount = PlacePrice.objects.filter(date=now(),
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
    return ajax_answer_lazy(payload)


def hotels_in_city(request):
    try:
        c = request.POST['city']
        path = request.POST['path'] or None
        if path:
            key = sha1('%s' % (path,)).hexdigest()
            data_key = cache.get(key)
            searched = Hotel.objects.filter(pk__in=data_key)
        else:
            city = City.objects.get(pk=c)
            searched = Hotel.objects.filter(Q(city=city) | Q(addon_city=city))
        return filter_hotels_on_map(request, searched)
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def hotels_in_country(request):
    try:
        searched = Hotel.objects.all()
        return filter_hotels_on_map(request, searched)
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def payment_method(request):
    try:
        p_m = request.POST['p_m']
        paymnt_method = PaymentMethod.objects.get(pk=p_m)
        payload = {'success': True, 'id': paymnt_method.pk, 'description': paymnt_method.description,
                   'card': paymnt_method.use_card}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def add_category(request):
    try:
        hotel_pk = request.POST['hotel']
        hotel = Hotel.objects.get(pk=hotel_pk)
        if request.user not in hotel.admins.all() and not request.user.is_superuser:
            raise UserNotAllowed
        category_name = request.POST['category_name']
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
    return ajax_answer_lazy(payload)


@transaction.atomic
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
                from_date += timedelta(days=1)
            booking_delete_client_mail(booking)
            booking.delete()
            url = reverse_lazy('bookings_list')
        elif action == 'enable':
            booking.enabled = True
            booking.save()
            booking_new_hotel_mail(booking)
            url = reverse_lazy('booking_admin_detail', args=[booking.uuid, ])
        else:
            raise UserNotAllowed
        payload = {'success': True, 'location': url}
    except UserNotAllowed:
        payload = {'success': False, 'error_msg': _('You are not allowed for this action.')}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def edit_discount(request):
    try:
        d = Discount.objects.get(pk=int(request.POST['discount']))
        if not request.user in d.hotel.admins.all() and not request.user.is_superuser:
            raise AccessError
        html = render_to_string('cabinet/edit_discount.html', {'discount': d})
        payload = {'success': True, 'html': html}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def delete_discount(request):
    try:
        d = Discount.objects.get(pk=int(request.POST['discount']))
        if not request.user in d.hotel.admins.all() and not request.user.is_superuser:
            raise AccessError
        d.delete()
        payload = {'success': True}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def add_room_discount(request):
    try:
        d = Discount.objects.get(pk=int(request.POST['discount']))
        if not request.user in d.hotel.admins.all() and not request.user.is_superuser:
            raise AccessError
        r = Room.objects.get(pk=int(request.POST['room']))
        if not RoomDiscount.objects.filter(room=r, discount=d).exists():
            RoomDiscount(room=r, discount=d, date=now()).save()
        payload = {'success': True}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def delete_room_discount(request):
    try:
        d = Discount.objects.get(pk=int(request.POST['discount']))
        if not request.user in d.hotel.admins.all() and not request.user.is_superuser:
            raise AccessError
        r = Room.objects.get(pk=int(request.POST['room']))
        RoomDiscount.objects.filter(room=r, discount=d).delete()
        payload = {'success': True}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)
