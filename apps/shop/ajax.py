# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404
from nnmware.apps.address.models import Country
from nnmware.apps.shop.models import Product, ProductParameterValue, ProductParameter, Basket, DeliveryAddress
from nnmware.core.ajax import AjaxLazyAnswer
from nnmware.core.http import get_session_from_request
from nnmware.core.imgutil import make_thumbnail
from nnmware.core.exceptions import AccessError


def autocomplete_search(request,size=16):
    results = []
    search_qs = Product.objects.filter(
        Q(name__icontains=request.REQUEST['q']) |
        Q(name_en__icontains=request.REQUEST['q'])).order_by('name')[:5]
    for r in search_qs:
        img = make_thumbnail(r.main_image,width=int(size))
        userstring = {'name': r.name, 'path': r.get_absolute_url(),
                      'img': img,
                      'slug': r.slug, 'amount':"%0.2f" % (r.amount,),'id':r.pk }
        results.append(userstring)
    payload = {'answer': results}
    return AjaxLazyAnswer(payload)

def add_param(request,object_id):
    try:
        if not request.user.is_superuser:
           raise AccessError
        p = get_object_or_404(Product,pk=int(object_id))
        ctype = ContentType.objects.get_for_model(Product)
        param = ProductParameterValue()
        param.content_type = ctype
        param.object_id = p.pk
        param.parameter = get_object_or_404(ProductParameter,pk=int(request.REQUEST['param']))
        param.value = request.REQUEST['value']
        if request.REQUEST['keyparam'] == 'on':
            param.keyparam = True
        param.save()
        try:
            unit = param.parameter.unit.name
        except :
            unit = ''
        payload = {'success': True, 'name':param.parameter.name, 'unit':unit, 'id': param.pk,
                   'value':param.value}
    except AccessError:
        payload = {'success': False}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def param_value_delete(request, object_id):
    # Link used when User delete the param value
    try:
        if not request.user.is_superuser:
            raise AccessError
        ProductParameterValue.objects.get(pk=int(object_id)).delete()
        payload = {'success': True}
    except AccessError:
        payload = {'success': False}
    except:
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def add_basket(request, object_id):
    # Link used when User add to basket
    try:
        p = Product.objects.get(pk=int(object_id))
        if not p.avail or p.quantity < 1 or p.amount <= 0 :
            raise AccessError
        if not request.user.is_authenticated():
            session_key = get_session_from_request(request)
            if Basket.objects.filter(session_key=session_key, product=p).count() >0 :
                b = Basket.objects.get(session_key=session_key, product=p)
                b.quantity += 1
            else:
                b = Basket(session_key=session_key,product=p)
                b.quantity = 1
            b.save()
            basket_user = Basket.objects.filter(session_key=session_key)
        else:
            if Basket.objects.filter(user=request.user, product=p).count() >0 :
                b = Basket.objects.get(user=request.user, product=p)
                b.quantity += 1
            else:
                b = Basket(user=request.user,product=p)
                b.quantity = 1
            b.save()
            basket_user = Basket.objects.filter(user=request.user)
        basket_count = basket_user.count()
        all_sum = 0
        for item in basket_user:
            all_sum += item.sum
        payload = {'success': True, 'basket_count':basket_count,
                   'basket_sum':"%0.2f" % (all_sum,)}
    except AccessError:
        payload = {'success': False}
    except:
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def delete_basket(request, object_id):
    # Link used when User delete the item from basket
    try:
        Basket.objects.get(pk=int(object_id)).delete()
        if request.user.is_authenticated():
            basket_user = Basket.objects.filter(user=request.user)
        else:
            basket_user = Basket.objects.filter(session_key=get_session_from_request(request))
        basket_count = basket_user.count()
        all_sum = 0
        for item in basket_user:
            all_sum += item.sum
        payload = {'success': True, 'basket_count':basket_count,
                   'basket_sum':"%0.2f" % (all_sum,),'id':int(object_id)}
    except AccessError:
        payload = {'success': False}
    except:
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def add_address(request, object_id):
    """
    Its Ajax add address in basket
    """
    try:
        if not request.user.is_authenticated():
            raise AccessError
        address = DeliveryAddress()
        address.user = request.user
        country_new = request.POST.get('country') or None
        if country_new is not None:
            country, created = Country.get_or_create(name=country_new)
            address.country = country

#        msg.subject = request.POST.get('message_subject') or None
#        msg.body = request.POST.get('message_body') or None
#        msg.sender = request.user
#        msg.recipient = User.objects.get(id=object_id)
#        msg.sent_at = datetime.now()

        address.save()
        payload = {'success': True}
#        , 'id':msg.pk, 'username':msg.sender.get_profile().get_name,
#                   'username_url':msg.sender.get_profile().get_absolute_url(),
#                   'message_subject':msg.subject, 'avatar_id':avatar_id,
#                   'message_date': message_date, 'message_body':msg.body }
    except AccessError:
        payload = {'success': False, 'error':_('You are not allowed for add address')}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)
