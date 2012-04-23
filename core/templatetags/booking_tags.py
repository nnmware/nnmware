# -*- coding: utf-8 -*-
import re

from django.template import Library
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.address.models import City
from nnmware.apps.booking.models import Hotel, TWO_STAR, THREE_STAR, FOUR_STAR, FIVE_STAR, HotelOption


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
def hotels_city():
    result = City.objects.all()
    return result

@register.assignment_tag
def hotels_best_offer():
    result = Hotel.objects.filter(best_offer=True)
    return result

@register.assignment_tag
def hotels_top10():
    result = Hotel.objects.filter(in_top10=True)
    return result
