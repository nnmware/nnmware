# -*- coding: utf-8 -*-
from django.db.models.query_utils import Q
from nnmware.apps.address.models import City
from nnmware.core.ajax import AjaxLazyAnswer


def autocomplete_city(request):
    search_qs = City.objects.filter(
        Q(name__icontains=request.REQUEST['q']) |
        Q(name_en__icontains=request.REQUEST['q'])).order_by('name')
    results = []
    for r in search_qs:
        userstring = {'name': r.get_name, 'slug': r.slug }
        results.append(userstring)
    payload = {'city': results}
    return AjaxLazyAnswer(payload)
