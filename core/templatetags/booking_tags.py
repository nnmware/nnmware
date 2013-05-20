# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from django.db.models import Min, Max, Count, Sum
from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.translation import gettext as _
from nnmware.apps.address.models import City
from nnmware.apps.booking.models import Hotel, TWO_STAR, THREE_STAR, FOUR_STAR, FIVE_STAR, \
    HotelOption, MINI_HOTEL, PlacePrice, Availability, HOSTEL, Discount
from nnmware.apps.money.models import ExchangeRate, Currency
from nnmware.core.config import OFFICIAL_RATE, CURRENCY
from nnmware.core.maps import distance_to_object
from nnmware.core.models import VisitorHit
from nnmware.core.utils import convert_to_date, daterange
from nnmware.apps.booking.models import APARTAMENTS


register = Library()


@register.assignment_tag
def apartaments_count(city=None):
    result = Hotel.objects.filter(starcount=APARTAMENTS).count()
    return result


@register.assignment_tag
def minihotel_count(city=None):
    result = Hotel.objects.filter(starcount=MINI_HOTEL).count()
    return result


@register.assignment_tag
def hostel_count(city=None):
    result = Hotel.objects.filter(starcount=HOSTEL).count()
    return result


@register.assignment_tag
def two_star_count(city=None):
    result = Hotel.objects.filter(starcount=TWO_STAR).count()
    return result


@register.assignment_tag
def three_star_count(city=None):
    result = Hotel.objects.filter(starcount=THREE_STAR).count()
    return result


@register.assignment_tag
def four_star_count(city=None):
    result = Hotel.objects.filter(starcount=FOUR_STAR).count()
    return result


@register.assignment_tag
def five_star_count(city=None):
    result = Hotel.objects.filter(starcount=FIVE_STAR).count()
    return result


@register.assignment_tag
def search_sticky_options():
    return HotelOption.objects.filter(sticky_in_search=True).order_by('order_in_list')


@register.assignment_tag
def search_options():
    return HotelOption.objects.filter(sticky_in_search=False, in_search=True).order_by('order_in_list')


@register.assignment_tag
def hotels_five_stars():
    result = Hotel.objects.filter(starcount=FIVE_STAR).select_related().order_by('name')
    return make_hotel_intro_list(result)


def make_hotel_intro_list(h_list):
    result = []
    arr_len = len(h_list)
    len_list, remainder = divmod(arr_len, 5)
    all_len = [len_list, len_list, len_list, len_list, len_list]
    for i in range(remainder):
        all_len[i] += 1
    for i in range(len(all_len)):
        result.append(h_list[:all_len[i]])
        h_list = h_list[all_len[i]:]
    return result


@register.assignment_tag
def hotels_four_stars():
    result = Hotel.objects.filter(starcount=FOUR_STAR).select_related()
    return make_hotel_intro_list(result)


@register.assignment_tag
def hotels_three_stars():
    result = Hotel.objects.filter(starcount=THREE_STAR).select_related()
    return make_hotel_intro_list(result)


@register.assignment_tag
def hotels_two_stars():
    result = Hotel.objects.filter(starcount=TWO_STAR).select_related()
    return make_hotel_intro_list(result)


@register.assignment_tag
def hotels_mini():
    result = Hotel.objects.filter(starcount=MINI_HOTEL).select_related()
    return make_hotel_intro_list(result)


@register.assignment_tag
def hotels_hostel():
    result = Hotel.objects.filter(starcount=HOSTEL).select_related()
    return make_hotel_intro_list(result)


@register.assignment_tag
def hotels_apartaments():
    result = Hotel.objects.filter(starcount=APARTAMENTS).select_related()
    return make_hotel_intro_list(result)


@register.assignment_tag
def hotels_city():
    result = City.objects.all()
    return result


@register.assignment_tag
def hotels_count():
    result = Hotel.objects.count()
    return result


@register.assignment_tag
def city_count():
    result = City.objects.count()
    return result


@register.assignment_tag
def hotels_best_offer():
    result = Hotel.objects.filter(best_offer=True).select_related().order_by('-current_amount')
    return result


@register.assignment_tag
def hotels_top10():
    city = City.objects.get(slug='moscow')
    result = Hotel.objects.filter(in_top10=True, city=city).select_related().order_by('-current_amount')
    return result


@register.simple_tag(takes_context=True)
def search_url(context):
    request = context['request']
    url = request.get_full_path()
    if url.count('&order'):
        url = url.split('&order')[0] + '&'
    elif url.count('?order'):
        url = url.split('?order')[0] + '?'
    else:
        if url[-1] == '/':
            url += '?'
        else:
            url += '&'
    return url


@register.simple_tag(takes_context=True)
def minprice_hotel_date(context, hotel, on_date):
    request = context['request']
    date = convert_to_date(on_date)
    hotel_price = hotel.amount_on_date(date)
    return amount_request_currency(request, hotel_price)


@register.simple_tag(takes_context=True)
def room_price_date(context, room, on_date):
    request = context['request']
    date = convert_to_date(on_date)
    room_price = room.amount_on_date(date)
    return amount_request_currency(request, room_price)


def dates_guests_from_context(context):
    search_data = context['search_data']
    f_date = search_data['from_date']
    t_date = search_data['to_date']
    guests = search_data['guests']
    from_date = convert_to_date(f_date)
    to_date = convert_to_date(t_date)
    delta = (to_date - from_date).days
    date_period = (from_date, to_date-timedelta(days=1))
    return from_date, to_date, date_period, delta, guests


@register.simple_tag(takes_context=True)
def room_price_average(context, room, rate):
    from_date, to_date, date_period, delta, guests = dates_guests_from_context(context)
    s = room.settlement_on_date_for_guests(from_date, guests)
    all_sum = PlacePrice.objects.filter(settlement__room=room, settlement__settlement=s, date__range=date_period).\
        aggregate(Sum('amount'))
    room_sum = all_sum['amount__sum']
    result = room_sum / delta
    return convert_to_client_currency(result, rate)


@register.simple_tag(takes_context=True)
def room_full_amount(context, room, rate):
    from_date, to_date, date_period, delta, guests = dates_guests_from_context(context)
    s = room.settlement_on_date_for_guests(from_date, guests)
    result = PlacePrice.objects.filter(settlement__room=room, settlement__settlement=s,
                                       date__range=date_period).aggregate(Sum('amount'))['amount__sum']
    return convert_to_client_currency(result, rate)


@register.simple_tag(takes_context=True)
def room_variant(context, room):
    from_date, to_date, date_period, delta, guests = dates_guests_from_context(context)
    return room.settlement_on_date_for_guests(from_date, guests)


@register.assignment_tag(takes_context=True)
def client_currency(context):
    request = context['request']
    try:
        currency = request.COOKIES['currency']
    except:
        currency = CURRENCY
    if currency == 'USD':
        return '$'
    elif currency == 'EUR':
        return '€'
    elif currency == 'JPY':
        return '¥'
    elif currency == 'GBP':
        return '£'
    else:
        return _('rub')


@register.simple_tag(takes_context=True)
def view_currency(context):
    request = context['request']
    try:
        currency = request.COOKIES['currency']
    except:
        currency = CURRENCY
    if currency == 'USD':
        return _('US Dollars')
    elif currency == 'EUR':
        return _('Euro')
    else:
        return _('Roubles')


@register.simple_tag
def convert_to_client_currency(amount, rate):
    try:
        if OFFICIAL_RATE:
            exchange = rate.official_rate
        else:
            exchange = rate.rate
        return int((amount * rate.nominal) / exchange)
    except:
        return int(amount)


def amount_request_currency(request, amount):
    try:
        currency = Currency.objects.get(code=request.COOKIES['currency'])
        rate = ExchangeRate.objects.filter(currency=currency).filter(date__lte=datetime.now()).order_by('-date')[0]
        if OFFICIAL_RATE:
            exchange = rate.official_rate
        else:
            exchange = rate.rate
        return int((amount * rate.nominal) / exchange)
    except:
        return int(amount)


@register.assignment_tag(takes_context=True)
def user_currency_rate(context):
    request = context['request']
    try:
        user_currency = request.COOKIES['currency']
    except:
        user_currency = CURRENCY
    try:
        rate = ExchangeRate.objects.select_related().filter(currency__code=user_currency).\
            filter(date__lte=datetime.now()).order_by('-date')[0]
        return rate
    except:
        return None


@register.simple_tag
def distance_for(origin, destiny):
    result = distance_to_object(origin, destiny)
    return format(result, '.2f')


@register.filter(is_safe=True)
@stringfilter
def rbtruncatechars(value, arg):
    """
    Truncates a string after a certain number of characters and add "..."
    """
    try:
        length = int(arg)
    except ValueError:  # Invalid literal for int().
        return value  # Fail silently.
    result = value[:length]
    while result[-1] == '.':
        result = result[:-1]
    return result + '...'


@register.filter
def min_3_days(d):
    return d - timedelta(days=3)


@register.simple_tag
def hotels_spb_count():
    city = City.objects.get(slug='spb')
    result = Hotel.objects.filter(city=city).count()
    return result


@register.simple_tag
def hotels_moscow_count():
    city = City.objects.get(slug='moscow')
    result = Hotel.objects.filter(city=city).count()
    return result


@register.assignment_tag
def hotels_city_count(slug):
    try:
        city = City.objects.get(slug=slug)
        result = Hotel.objects.filter(city=city).count()
        return result
    except:
        return 0


@register.assignment_tag
def settlement_prices_on_dates(settlement, dates):
    prices = PlacePrice.objects.filter(settlement=settlement, date__in=dates).values_list('date', 'amount').\
        order_by('date')
    result = dict((d, '') for d in dates)
    for d, amount in prices:
        result[d] = amount
    return result


@register.assignment_tag
def discount_on_dates(room, dates):
    result = Discount.objects.filter(room=room, date__in=dates).order_by('date')
    return result


@register.assignment_tag
def room_availability_on_dates(room, dates):
    result = Availability.objects.filter(room=room, date__in=dates).order_by('date')
    return result


@register.assignment_tag
def room_min_days_on_dates(room, dates):
    result = Availability.objects.filter(room=room, date__in=dates).order_by('date')
    return result


@register.simple_tag
def today_visitor_count():
    result = set(VisitorHit.objects.values_list('session_key', flat=True))
    #    result = VisitorHit.objects.filter(date__lte=datetime.now().date()-timedelta(days=1),
    #        date__gte=datetime.now().date()-timedelta(days=30)).values_list('session_key', flat=True).distinct()
    return len(result)


@register.simple_tag
def today_hit_count():
    return VisitorHit.objects.count()

#    return VisitorHit.objects.filter(date__lte=datetime.now().date()-timedelta(days=1),
#        date__gte=datetime.now().date()-timedelta(days=30)).count()


@register.simple_tag
def room_avg_amount(amount, days):
    result = amount / days
    return format(result, '.2f')


@register.assignment_tag(takes_context=True)
def min_hotel_price(context):
    request = context['request']
    result = PlacePrice.objects.filter(amount__gt=0).aggregate(Min('amount'))
    return amount_request_currency(request, int(result['amount__min']))


@register.assignment_tag(takes_context=True)
def max_hotel_price(context):
    request = context['request']
    result = PlacePrice.objects.aggregate(Max('amount'))
    return amount_request_currency(request, int(result['amount__max']))


@register.assignment_tag
def hotel_range_price(rate):
    result = PlacePrice.objects.filter(amount__gt=0).aggregate(Min('amount'), Max('amount'))
    return convert_to_client_currency(int(result['amount__min']), rate), \
        convert_to_client_currency(int(result['amount__max']), rate)


@register.assignment_tag
def stars_hotel_count():
    result = Hotel.objects.values('starcount').order_by('starcount').annotate(Count('starcount'))
    return result
