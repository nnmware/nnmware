# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from nnmware.apps.shop.models import Product
from nnmware.core.ajax import AjaxLazyAnswer
from nnmware.core.imgutil import make_thumbnail


def autocomplete_search(request,width=16):
    results = []
    search_qs = Product.objects.filter(
        Q(name__icontains=request.REQUEST['q']) |
        Q(name_en__icontains=request.REQUEST['q'])).order_by('name')[:5]
    for r in search_qs:
        img = make_thumbnail(r.main_image,width=width)
        url = reverse('product_detail', args=[r.pk])
        userstring = {'name': r.name, 'path': url,
                      'img': img,
                      'slug': r.slug, 'amount':r.amount }
        results.append(userstring)
    payload = {'answer': results}
    return AjaxLazyAnswer(payload)
