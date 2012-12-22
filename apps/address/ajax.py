# -*- coding: utf-8 -*-
from django.db.models.query_utils import Q
from nnmware.apps.address.models import City, Country, Region
from nnmware.core.ajax import AjaxLazyAnswer

def base_autocomplete(search_qs):
    results = []
    for r in search_qs:
        userstring = {'name': r.get_name, 'slug': r.slug }
        results.append(userstring)
    payload = {'answer': results}
    return AjaxLazyAnswer(payload)

def autocomplete_city(request):
    search_qs = City.objects.filter(
        Q(name__icontains=request.REQUEST['q']) |
        Q(name_en__icontains=request.REQUEST['q'])).order_by('name')
    return base_autocomplete(search_qs)

def autocomplete_country(request):
    search_qs = Country.objects.filter(
        Q(name__icontains=request.REQUEST['q']) |
        Q(name_en__icontains=request.REQUEST['q'])).order_by('name')
    return base_autocomplete(search_qs)

def autocomplete_region(request):
    search_qs = Region.objects.filter(
        Q(name__icontains=request.REQUEST['q']) |
        Q(name_en__icontains=request.REQUEST['q'])).order_by('name')
    return base_autocomplete(search_qs)

