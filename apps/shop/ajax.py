# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404
from nnmware.apps.shop.models import Product, ProductParameterValue
from nnmware.core.ajax import AjaxLazyAnswer
from nnmware.core.imgutil import make_thumbnail


def autocomplete_search(request,size=16):
    results = []
    search_qs = Product.objects.filter(
        Q(name__icontains=request.REQUEST['q']) |
        Q(name_en__icontains=request.REQUEST['q'])).order_by('name')[:5]
    for r in search_qs:
        img = make_thumbnail(r.main_image,width=int(size))
        userstring = {'name': r.name, 'path': r.get_absolute_url(),
                      'img': img,
                      'slug': r.slug, 'amount':"%0.2f" % (r.amount,) }
        results.append(userstring)
    payload = {'answer': results}
    return AjaxLazyAnswer(payload)

def add_param(request,object_id):
    try:
        p = get_object_or_404(Product,pk=int(object_id))
        ctype = ContentType.objects.get_for_model(Product)
        param = ProductParameterValue()
        param.content_type = ctype
        param.object_id = p.pk
        param.user_agent = request.META['HTTP_USER_AGENT']

        payload = {'success': True}
    except :
        payload = {'success': False}

    return AjaxLazyAnswer(payload)
