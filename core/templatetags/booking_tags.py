# -*- coding: utf-8 -*-
from datetime import datetime
import re

from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.address.models import City
from nnmware.apps.booking.models import Hotel, TWO_STAR, THREE_STAR, FOUR_STAR, FIVE_STAR, HotelOption, MINI_HOTEL
from nnmware.apps.money.models import ExchangeRate, Currency
from nnmware.core.config import OFFICIAL_RATE, CURRENCY
from nnmware.core.maps import distance_to_object
from nnmware.core.utils import convert_to_date


register = Library()

@register.simple_tag
def two_star_count(city=None):
    result = Hotel.objects.filter(starcount=TWO_STAR).count()
    return result

@register.simple_tag
def three_star_count(city=None):
    result = Hotel.objects.filter(starcount=THREE_STAR).count()
    return result

@register.simple_tag
def four_star_count(city=None):
    result = Hotel.objects.filter(starcount=FOUR_STAR).count()
    return result

@register.simple_tag
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
    result = Hotel.objects.filter(starcount=FIVE_STAR)
    return result

@register.assignment_tag
def hotels_four_stars():
    result = Hotel.objects.filter(starcount=FOUR_STAR)
    return result

@register.assignment_tag
def hotels_three_stars():
    result = Hotel.objects.filter(starcount=THREE_STAR)
    return result

@register.assignment_tag
def hotels_two_stars():
    result = Hotel.objects.filter(starcount=TWO_STAR)
    return result

@register.assignment_tag
def hotels_mini():
    result = Hotel.objects.filter(starcount=MINI_HOTEL)
    return result

@register.assignment_tag
def hotels_city():
    result = City.objects.all()
    return result

@register.simple_tag
def hotels_count():
    result = Hotel.objects.count()
    return result

@register.assignment_tag
def hotels_best_offer():
    result = Hotel.objects.filter(best_offer=True)
    return result

@register.assignment_tag
def hotels_top10():
    result = Hotel.objects.filter(in_top10=True)
    return result

@register.simple_tag(takes_context = True)
def search_url(context):
    request = context['request']
    url = request.get_full_path()
    if url.count('&order'):
        url = url.split('&order')[0]+'&'
    elif url.count('?order'):
        url = url.split('?order')[0]+'?'
    else:
        if url[-1] == '/':
            url += '?'
        else:
            url += '&'
    return url

@register.simple_tag(takes_context = True)
def minprice_hotel_date(context, hotel, on_date):
    request = context['request']
    date = convert_to_date(on_date)
    hotel_price = hotel.amount_on_date(date)
    try:
        currency = Currency.objects.get(code=request.COOKIES['currency'])
        rate = ExchangeRate.objects.filter(currency=currency).filter(date__lte=datetime.now()).order_by('-date')[0]
        if OFFICIAL_RATE:
            exchange = rate.official_rate
        else:
            exchange = rate.rate
        result = (hotel_price*rate.nominal)/exchange
    except :
        result = hotel_price
    return int(result)

@register.simple_tag(takes_context = True)
def room_price_date(context, room, on_date):
    request = context['request']
    date = convert_to_date(on_date)
    room_price = room.amount_on_date(date)
    try:
        currency = Currency.objects.get(code=request.COOKIES['currency'])
        rate = ExchangeRate.objects.filter(currency=currency).filter(date__lte=datetime.now()).order_by('-date')[0]
        if OFFICIAL_RATE:
            exchange = rate.official_rate
        else:
            exchange = rate.rate
        result = (room_price*rate.nominal)/exchange
    except :
        result = room_price
    return int(result)

@register.simple_tag(takes_context = True)
def client_currency(context):
    request = context['request']
    try:
        currency = request.COOKIES['currency']
    except :
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

@register.simple_tag
def distance_for(origin, destiny):
    result = distance_to_object(origin,destiny)
    return format(result, '.2f')

@register.filter(is_safe=True)
@stringfilter
def rbtruncatechars(value, arg):
    """
    Truncates a string after a certain number of characters and add "..."
    """
    try:
        length = int(arg)
    except ValueError: # Invalid literal for int().
        return value # Fail silently.
    result = value[:length]
    while result[-1] == '.':
        result = result[:-1]
    return result+'...'
