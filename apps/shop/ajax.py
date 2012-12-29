# -*- coding: utf-8 -*-
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from nnmware.apps.address.models import Country, Region, City
from nnmware.apps.shop.models import Product, ProductParameterValue, ProductParameter, Basket, DeliveryAddress, Order, \
    STATUS_WAIT, OrderItem, Feedback, ProductColor, ProductMaterial
from nnmware.core.ajax import AjaxLazyAnswer
from nnmware.core.http import get_session_from_request
from nnmware.core.imgutil import make_thumbnail
from nnmware.core.exceptions import AccessError
from nnmware.core.models import Nnmcomment
from nnmware.core.utils import send_template_mail
import settings

class BasketError(Exception):
    pass

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

def add_address(request):
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
            country, created = Country.objects.get_or_create(name=country_new)
            address.country = country
        region_new = request.POST.get('region') or None
        if region_new is not None:
            region, created = Region.objects.get_or_create(name=region_new)
            address.region = region
        zipcode = request.POST.get('zipcode') or None
        if zipcode is not None:
            address.zipcode = zipcode
        city_new = request.POST.get('city') or None
        if city_new is not None:
            city, created = City.objects.get_or_create(name=city_new)
            address.city = city
        street = request.POST.get('street') or None
        if street is not None:
            address.street = street
        house_number = request.POST.get('house_number') or None
        if house_number is not None:
            address.house_number = house_number
        building = request.POST.get('building') or None
        if building is not None:
            address.building = building
        flat_number = request.POST.get('flat_number') or None
        if flat_number is not None:
            address.flat_number = flat_number
        first_name = request.POST.get('first_name') or None
        if first_name is not None:
            address.first_name = first_name
        middle_name = request.POST.get('middle_name') or None
        if middle_name is not None:
            address.middle_name = middle_name
        last_name = request.POST.get('last_name') or None
        if last_name is not None:
            address.last_name = last_name
        phone = request.POST.get('phone') or None
        if phone is not None:
            address.phone = phone
        skype = request.POST.get('skype') or None
        if skype is not None:
            address.skype = skype
        address.save()
        payload = {'success': True}
    except AccessError:
        payload = {'success': False, 'error':_('You are not allowed for add address')}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def delete_address(request, object_id):
    # Link used when User delete the address delivery
    try:
        if not request.user.is_authenticated():
            raise AccessError
        DeliveryAddress.objects.get(pk=int(object_id)).delete()
        payload = {'success': True,'id':int(object_id)}
    except AccessError:
        payload = {'success': False}
    except:
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def check_basket(user):
    basket = Basket.objects.filter(user=user)
    if basket.count() < 1:
        return False
    for item in basket:
        if item.quantity > item.product.quantity or item.product.avail is False:
            return False
    return True

def new_order(request):
    # Link used when User make order
    try:
        if not request.user.is_authenticated():
            raise AccessError
        if not check_basket(request.user):
            raise BasketError
        addr = request.POST.get('addr')
        address = DeliveryAddress.objects.get(user=request.user, pk=int(addr))
        order = Order()
        order.address = str(address)
        order.first_name = address.first_name
        order.middle_name = address.middle_name
        order.last_name = address.last_name
        order.user = request.user
        order.name = ''
        order.comment = ''
        order.status = STATUS_WAIT
        order.save()
        basket = Basket.objects.filter(user=request.user)
        for item in basket:
            order_item = OrderItem()
            order_item.order = order
            order_item.product_name = item.product.name
            order_item.product_origin = item.product
            order_item.product_url = item.product.get_absolute_url
            order_item.amount = item.product.amount
            order_item.product_pn = item.product.shop_pn
            order_item.quantity = item.quantity
            order_item.save()
            item.product.quantity -= item.quantity
            item.product.save()
        basket.delete()
        recipients = [settings.SHOP_MANAGER]
        mail_dict = {'order': order}
        subject = 'emails/neworder_admin_subject.txt'
        body = 'emails/neworder_admin_body.txt'
        send_template_mail(subject,body,mail_dict,recipients)
        try:
            recipients = [request.user.email]
            mail_dict = {'order': order}
            subject = 'emails/neworder_client_subject.txt'
            body = 'emails/neworder_client_body.txt'
            send_template_mail(subject,body,mail_dict,recipients)
        except:
            pass
        payload = {'success': True,'id':order.pk, 'location':order.get_absolute_url()}
    except AccessError:
        payload = {'success': False}
    except BasketError:
        payload = {'success': False, 'message':_('Product in basket not available')}
    except:
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def push_feedback(request):
    """
    Its Ajax posted feedback
    """
    try:
        msg = Feedback()
        msg.ip = request.META['REMOTE_ADDR']
        msg.user_agent = request.META['HTTP_USER_AGENT']
        msg.name = request.POST.get('name')
        msg.email = request.POST.get('email')
        msg.message = request.POST.get('message')
        msg.save()
        payload = {'success': True}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def push_answer(request,object_id):
    try:
        f = Feedback.objects.get(pk=int(object_id))
        f.answer = request.POST.get('answer')
        recipients = [f.email]
        mail_dict = {'feedback': f}
        subject = 'emails/feedback_answer_subject.txt'
        body = 'emails/feedback_answer_body.txt'
        send_template_mail(subject,body,mail_dict,recipients)
        f.save()
        payload = {'success': True, 'location': f.get_absolute_url()}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def delete_product(request, object_id):
    # Link used when User delete the product
    try:
        if not request.user.is_superuser:
            raise AccessError
        p = Product.objects.get(pk=int(object_id))
        p.visible = False
        p.save()
        payload = {'success': True}
    except AccessError:
        payload = {'success': False}
    except:
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def delete_feedback(request, object_id):
    # Link used when User delete the feedback
    try:
        if not request.user.is_superuser:
            raise AccessError
        Feedback.objects.get(pk=int(object_id)).delete()
        payload = {'success': True}
    except AccessError:
        payload = {'success': False}
    except:
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def delete_comment(request, object_id):
    # Link used when Admin delete the comment
    try:
        if not request.user.is_superuser:
            raise AccessError
        Nnmcomment.objects.get(pk=int(object_id)).delete()
        payload = {'success': True}
    except AccessError:
        payload = {'success': False}
    except:
        payload = {'success': False}
    return AjaxLazyAnswer(payload)


def add_color(request,object_id):
    try:
        if not request.user.is_superuser:
            raise AccessError
        p = get_object_or_404(Product,pk=int(object_id))
        color = get_object_or_404(ProductColor,pk=int(request.REQUEST['color']))
        w = int(request.REQUEST['width'])
        h = int(request.REQUEST['height'])
        p.colors.add(color)
        p.save()
        payload = {'success': True, 'name':color.name, 'id': color.pk,
                   'src': make_thumbnail(color.img.url,width=w,height=h)}
    except AccessError:
        payload = {'success': False}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def delete_color(request,object_id, color_id):
    try:
        if not request.user.is_superuser:
            raise AccessError
        p = get_object_or_404(Product,pk=int(object_id))
        color = get_object_or_404(ProductColor,pk=int(color_id))
        p.colors.remove(color)
        p.save()
        payload = {'success': True}
    except AccessError:
        payload = {'success': False}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def add_material(request,object_id):
    try:
        if not request.user.is_superuser:
            raise AccessError
        p = get_object_or_404(Product,pk=int(object_id))
        material = get_object_or_404(ProductMaterial,pk=int(request.REQUEST['material']))
        p.materials.add(material)
        p.save()
        payload = {'success': True, 'name':material.name, 'id': material.pk}
    except AccessError:
        payload = {'success': False}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def delete_material(request,object_id, material_id):
    try:
        if not request.user.is_superuser:
            raise AccessError
        p = get_object_or_404(Product,pk=int(object_id))
        material = get_object_or_404(ProductMaterial,pk=int(material_id))
        p.materials.remove(material)
        p.save()
        payload = {'success': True}
    except AccessError:
        payload = {'success': False}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def add_related_product(request,object_id):
    try:
        if not request.user.is_superuser:
            raise AccessError
        p = get_object_or_404(Product,pk=int(object_id))
        product = get_object_or_404(Product,pk=int(request.REQUEST['product']))
        p.related_products.add(product)
        p.save()
        payload = {'success': True, 'name':product.name, 'id': product.pk, 'url':product.get_absolute_url(),
                   'src': make_thumbnail(product.main_image,width=settings.RELATED_PRODUCT_WIDTH,height=settings.RELATED_PRODUCT_HEIGHT)}
    except AccessError:
        payload = {'success': False}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def delete_related_product(request,object_id, product_id):
    try:
        if not request.user.is_superuser:
            raise AccessError
        p = get_object_or_404(Product,pk=int(object_id))
        product = get_object_or_404(Product,pk=int(product_id))
        p.related_products.remove(product)
        p.save()
        payload = {'success': True}
    except AccessError:
        payload = {'success': False}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)
