# nnmware(c)2012-2016

from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from nnmware.apps.address.models import Country, Region, City
from nnmware.apps.market.models import Product, ProductParameterValue, ProductParameter, Basket, DeliveryAddress, \
    Feedback, ProductColor, ProductMaterial
from nnmware.core.ajax import ajax_answer_lazy
from nnmware.core.http import get_session_from_request
from nnmware.core.imgutil import make_thumbnail
from nnmware.core.exceptions import AccessError
from nnmware.core.models import Nnmcomment
from nnmware.core.utils import send_template_mail
from nnmware.apps.market.models import MarketCallback
import settings


class BasketError(Exception):
    pass


def autocomplete_search(request, size=16):
    results = []
    search_qs = Product.objects.filter(
        Q(name__icontains=request.POST['q']) |
        Q(name_en__icontains=request.POST['q'])).order_by('name')[:5]
    for r in search_qs:
        img = make_thumbnail(r.main_image, width=int(size))
        userstring = {'name': r.name, 'path': r.get_absolute_url(),
                      'img': img,
                      'slug': r.slug, 'amount': "%0.2f" % (r.amount,), 'id': r.pk}
        results.append(userstring)
    payload = {'answer': results}
    return ajax_answer_lazy(payload)


def add_param(request, object_id):
    # noinspection PyBroadException
    try:
        if not request.user.is_superuser:
            raise AccessError
        p = get_object_or_404(Product, pk=int(object_id))
        ctype = ContentType.objects.get_for_model(Product)
        param = ProductParameterValue()
        param.content_type = ctype
        param.object_id = p.pk
        param.parameter = get_object_or_404(ProductParameter, pk=int(request.POST['param']))
        param.value = request.POST['value']
        if request.POST['keyparam'] == 'on':
            param.keyparam = True
        param.save()
        # noinspection PyBroadException
        try:
            unit = param.parameter.unit.name
        except:
            unit = ''
        payload = {'success': True, 'name': param.parameter.name, 'unit': unit, 'id': param.pk,
                   'value': param.value}
    except AccessError as aerr:
        payload = {'success': False}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def param_value_delete(request, object_id):
    # Link used when User delete the param value
    # noinspection PyBroadException
    try:
        if not request.user.is_superuser:
            raise AccessError
        ProductParameterValue.objects.get(pk=int(object_id)).delete()
        payload = {'success': True}
    except AccessError as aerr:
        payload = {'success': False}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def add_basket(request, object_id):
    # Link used when User add to basket
    # noinspection PyBroadException
    try:
        p = Product.objects.get(pk=int(object_id))
        if not p.avail or p.quantity < 1 or p.amount <= 0:
            raise AccessError
        # noinspection PyBroadException
        try:
            color_id = request.POST['color']
            color = ProductColor.objects.get(pk=int(color_id))
            addon_text = color.name
        except:
            addon_text = ''
        if not request.user.is_authenticated():
            session_key = get_session_from_request(request)
            if Basket.objects.filter(session_key=session_key, product=p, addon=addon_text).count() > 0:
                b = Basket.objects.get(session_key=session_key, product=p, addon=addon_text)
                b.quantity += 1
            else:
                b = Basket(session_key=session_key, product=p, addon=addon_text)
                b.quantity = 1
            b.save()
            basket_user = Basket.objects.filter(session_key=session_key)
        else:
            if Basket.objects.filter(user=request.user, product=p, addon=addon_text).count() > 0:
                b = Basket.objects.get(user=request.user, product=p, addon=addon_text)
                b.quantity += 1
            else:
                b = Basket(user=request.user, product=p, addon=addon_text)
                b.quantity = 1
            b.save()
            basket_user = Basket.objects.filter(user=request.user)
        basket_count = basket_user.count()
        all_sum = 0
        for item in basket_user:
            all_sum += item.sum
        payload = {'success': True, 'basket_count': basket_count,
                   'basket_sum': "%0.2f" % (all_sum,)}
    except AccessError as aerr:
        payload = {'success': False}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def delete_basket(request, object_id):
    # Link used when User delete the item from basket
    # noinspection PyBroadException
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
        payload = {'success': True, 'basket_count': basket_count,
                   'basket_sum': "%0.2f" % (all_sum,), 'id': int(object_id)}
    except AccessError as aerr:
        payload = {'success': False}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def add_address(request):
    """
    Its Ajax add address in basket
    """
    # noinspection PyBroadException
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
    except AccessError as aerr:
        payload = {'success': False, 'error': _('You are not allowed for add address')}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def delete_address(request, object_id):
    # Link used when User delete the address delivery
    # noinspection PyBroadException
    try:
        if not request.user.is_authenticated():
            raise AccessError
        DeliveryAddress.objects.get(pk=int(object_id)).delete()
        payload = {'success': True, 'id': int(object_id)}
    except AccessError as aerr:
        payload = {'success': False}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def push_feedback(request):
    """
    Its Ajax posted feedback
    """
    # noinspection PyBroadException
    try:
        msg = Feedback()
        msg.ip = request.META['REMOTE_ADDR']
        msg.user_agent = request.META['HTTP_USER_AGENT']
        msg.name = request.POST.get('name')
        msg.email = request.POST.get('email')
        msg.message = request.POST.get('message')
        msg.save()
        payload = {'success': True}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def push_answer(request, object_id):
    # noinspection PyBroadException
    try:
        f = Feedback.objects.get(pk=int(object_id))
        f.answer = request.POST.get('answer')
        recipients = [f.email]
        mail_dict = {'feedback': f}
        subject = 'emails/feedback_answer_subject.txt'
        body = 'emails/feedback_answer_body.txt'
        send_template_mail(subject, body, mail_dict, recipients)
        f.save()
        payload = {'success': True, 'location': f.get_absolute_url()}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def delete_product(request, object_id):
    # Link used when User delete the product
    # noinspection PyBroadException
    try:
        if not request.user.is_superuser:
            raise AccessError
        p = Product.objects.get(pk=int(object_id))
        p.visible = False
        p.save()
        payload = {'success': True}
    except AccessError as aerr:
        payload = {'success': False}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def delete_feedback(request, object_id):
    # Link used when User delete the feedback
    # noinspection PyBroadException
    try:
        if not request.user.is_superuser:
            raise AccessError
        Feedback.objects.get(pk=int(object_id)).delete()
        payload = {'success': True}
    except AccessError as aerr:
        payload = {'success': False}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def delete_comment(request, object_id):
    # Link used when Admin delete the comment
    # noinspection PyBroadException
    try:
        if not request.user.is_superuser:
            raise AccessError
        Nnmcomment.objects.get(pk=int(object_id)).delete()
        payload = {'success': True}
    except AccessError as aerr:
        payload = {'success': False}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def add_color(request, object_id):
    # noinspection PyBroadException
    try:
        if not request.user.is_superuser:
            raise AccessError
        p = get_object_or_404(Product, pk=int(object_id))
        color = get_object_or_404(ProductColor, pk=int(request.POST['color']))
        w = int(request.POST['width'])
        h = int(request.POST['height'])
        p.colors.add(color)
        p.save()
        payload = {'success': True, 'name': color.name, 'id': color.pk,
                   'src': make_thumbnail(color.img.url, width=w, height=h)}
    except AccessError as aerr:
        payload = {'success': False}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def delete_color(request, object_id, color_id):
    # noinspection PyBroadException
    try:
        if not request.user.is_superuser:
            raise AccessError
        p = get_object_or_404(Product, pk=int(object_id))
        color = get_object_or_404(ProductColor, pk=int(color_id))
        p.colors.remove(color)
        p.save()
        payload = {'success': True}
    except AccessError as aerr:
        payload = {'success': False}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def add_material(request, object_id):
    # noinspection PyBroadException
    try:
        if not request.user.is_superuser:
            raise AccessError
        p = get_object_or_404(Product, pk=int(object_id))
        material = get_object_or_404(ProductMaterial, pk=int(request.POST['material']))
        p.materials.add(material)
        p.save()
        payload = {'success': True, 'name': material.name, 'id': material.pk}
    except AccessError as aerr:
        payload = {'success': False}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def delete_material(request, object_id, material_id):
    # noinspection PyBroadException
    try:
        if not request.user.is_superuser:
            raise AccessError
        p = get_object_or_404(Product, pk=int(object_id))
        material = get_object_or_404(ProductMaterial, pk=int(material_id))
        p.materials.remove(material)
        p.save()
        payload = {'success': True}
    except AccessError as aerr:
        payload = {'success': False}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def add_related_product(request, object_id):
    # noinspection PyBroadException
    try:
        if not request.user.is_superuser:
            raise AccessError
        p = get_object_or_404(Product, pk=int(object_id))
        product = get_object_or_404(Product, pk=int(request.POST['product']))
        p.related_products.add(product)
        p.save()
        payload = {'success': True, 'name': product.name, 'id': product.pk, 'url': product.get_absolute_url(),
                   'src': make_thumbnail(product.main_image, width=settings.RELATED_PRODUCT_WIDTH,
                                         height=settings.RELATED_PRODUCT_HEIGHT, aspect=1)}
    except AccessError as aerr:
        payload = {'success': False}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def delete_related_product(request, object_id, product_id):
    # noinspection PyBroadException
    try:
        if not request.user.is_superuser:
            raise AccessError
        p = get_object_or_404(Product, pk=int(object_id))
        product = get_object_or_404(Product, pk=int(product_id))
        p.related_products.remove(product)
        p.save()
        payload = {'success': True}
    except AccessError as aerr:
        payload = {'success': False}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def basket_avail(user):
    basket = Basket.objects.filter(user=user)
    if basket.count() < 1:
        return False
    for item in basket:
        if item.quantity > item.product.quantity or item.product.avail is False:
            return False
    return True


def add_compare_product(request, object_id):
    # noinspection PyBroadException
    try:
        compare = request.session['market_compare']
    except:
        compare = []
    product_id = int(object_id)
    if product_id not in compare:
        compare.append(product_id)
    # noinspection PyBroadException
    try:
        request.session['market_compare'] = compare
        payload = {'success': True}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def del_compare_product(request, object_id):
    # noinspection PyBroadException
    try:
        compare = request.session['market_compare']
    except:
        compare = []
    product_id = int(object_id)
    if product_id in compare:
        compare.remove(product_id)
    # noinspection PyBroadException
    try:
        request.session['market_compare'] = compare
        payload = {'success': True}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def push_marketcallback(request):
    """
    Its Ajax posted market callback
    """
    # noinspection PyBroadException
    try:
        cb = MarketCallback()
        cb.ip = request.META['REMOTE_ADDR']
        cb.user_agent = request.META['HTTP_USER_AGENT']
        cb.clientname = request.POST.get('clientname')
        cb.clientphone = request.POST.get('clientphone')
        cb.save()
        mail_dict = {'callback': cb}
        recipients = [settings.MARKET_MANAGER]
        subject = 'emails/callback_admin_subject.txt'
        body = 'emails/callback_admin_body.txt'
        send_template_mail(subject, body, mail_dict, recipients)
        payload = {'success': True}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def push_quickorder(request):
    """
    Its Ajax posted market quick order
    """
    # noinspection PyBroadException
    try:
        cb = MarketCallback()
        cb.ip = request.META['REMOTE_ADDR']
        cb.user_agent = request.META['HTTP_USER_AGENT']
        cb.clientname = request.POST.get('clientname')
        cb.clientphone = request.POST.get('clientphone')
        cb.description = request.POST.get('product_url')
        cb.quickorder = True
        cb.save()
        mail_dict = {'callback': cb}
        recipients = [settings.MARKET_MANAGER]
        subject = 'emails/quickorder_admin_subject.txt'
        body = 'emails/quickorder_admin_body.txt'
        send_template_mail(subject, body, mail_dict, recipients)
        payload = {'success': True}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)
