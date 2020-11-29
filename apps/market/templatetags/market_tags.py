# nnmware(c)2012-2020

from datetime import timedelta
from xml.etree.ElementTree import Element, SubElement, tostring

from django.template import Library
from django.template.defaultfilters import floatformat

from nnmware.apps.market.models import Basket, Product, Order, OrderItem, ProductCategory, SpecialOffer, Review, \
    MarketSlider
from nnmware.core.http import get_session_from_request


register = Library()


def _get_basket(request):
    if request.user.is_authenticated:
        Basket.objects.filter(session_key=get_session_from_request(request)).update(user=request.user)
        return Basket.objects.filter(user=request.user)
    else:
        return Basket.objects.filter(session_key=get_session_from_request(request))


@register.simple_tag(takes_context=True)
def basket(context):
    request = context['request']
    return _get_basket(request)


@register.simple_tag
def latest_products():
    return Product.objects.latest()


@register.simple_tag(takes_context=True)
def basket_sum(context):
    result = basket(context)
    all_sum = 0
    for item in result:
        all_sum += item.sum
    return all_sum


@register.simple_tag(takes_context=True)
def basket_count(context):
    items = basket(context)
    result = 0
    for item in items:
        result += item.quantity
    return result


@register.simple_tag
def order_date_sum(on_date):
    result = 0
    on_day = Order.objects.active().filter(created_date__range=(on_date, on_date + timedelta(days=1)))
    for item in on_day:
        result += item.fullamount
    return floatformat(result, 0)


@register.simple_tag
def order_date_avg(on_date):
    result = 0
    on_day = Order.objects.active().filter(created_date__range=(on_date, on_date + timedelta(days=1)))
    for item in on_day:
        result += item.fullamount
    return floatformat(result / on_day.count(), 0)


@register.simple_tag
def sales_sum(product_pk, on_date):
    result = 0
    p = Product.objects.get(pk=product_pk)
    on_day = Order.objects.active().filter(created_date__range=(on_date, on_date + timedelta(days=1)))
    res = OrderItem.objects.filter(order__in=on_day, product_origin=p)
    for item in res:
        result += item.quantity
    return result


@register.simple_tag
def menu_market():
    if 1 > 0:  # try:
        html = Element("ul")
        for node in ProductCategory.objects.all():
            if not node.parent:
                menu_recurse_market(node, html)
        return tostring(html, 'unicode')

#    except:
#        return 'error'


def menu_recurse_market(current_node, parent_node, show_empty=True):
    child_count = current_node.children.count()

    if show_empty or child_count > 0:
        temp_parent = SubElement(parent_node, 'li')
        attrs = {'href': current_node.get_absolute_url(), 'class': 'cat' + str(int(current_node.pk))}
        link = SubElement(temp_parent, 'a', attrs)
        cat_name = SubElement(link, 'span')
        cat_name.text = current_node.get_name
        counter = current_node.obj_active_set.count()
        for child in current_node.get_all_children():
            counter += child.obj_active_set.count()
            #        if counter > 0:
        #            count_txt = SubElement(link, 'sup')
        #            count_txt.text = ' ' + str(counter)
        if child_count > 0:
            new_parent = SubElement(temp_parent, 'ul', {'class': 'subcat'})
            children = current_node.children.order_by('position', 'name')
            for child in children:
                menu_recurse_market(child, new_parent)


@register.simple_tag
def market_parent():
    return ProductCategory.objects.filter(parent=None).order_by('position')


@register.simple_tag
def special_offer():
    return SpecialOffer.objects.all().order_by('?')


@register.simple_tag
def market_reviews():
    result = []
    # noinspection PyBroadException
    try:
        vip = Review.objects.filter(vip=True).order_by('?')[0]
        result.append(vip)
    except:
        pass
    user_review = Review.objects.filter(vip=False).order_by('?')[:10]
    result += user_review
    return result


@register.simple_tag
def main_page_products():
    return Product.objects.on_main()


@register.simple_tag(takes_context=True)
def compare_products(context):
    request = context['request']
    # noinspection PyBroadException
    try:
        compare = request.session['market_compare']
        return Product.objects.filter(pk__in=compare)
    except:
        return None


@register.simple_tag
def market_slider():
    return MarketSlider.objects.filter(visible=True)
