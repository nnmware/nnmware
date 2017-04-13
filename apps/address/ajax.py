# nnmware(c)2012-2017

from __future__ import unicode_literals

from django.db.models.query_utils import Q

from nnmware.apps.address.models import City, Country, Region, StationMetro
from nnmware.core.ajax import ajax_answer_lazy


def base_autocomplete(obj, request):
    search_qs = obj.objects.filter(
        Q(name__icontains=request.POST['q']) |
        Q(name_en__icontains=request.POST['q'])).order_by('name')
    results = []
    for r in search_qs:
        userstring = {'name': r.get_name, 'slug': r.slug}
        results.append(userstring)
    payload = {'answer': results}
    return ajax_answer_lazy(payload)


def autocomplete_city(request):
    return base_autocomplete(City, request)


def autocomplete_country(request):
    return base_autocomplete(Country, request)


def autocomplete_region(request):
    return base_autocomplete(Region, request)


def autocomplete_stationmetro(request):
    return base_autocomplete(StationMetro, request)
