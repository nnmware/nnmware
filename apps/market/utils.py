# nnmware(c)2012-2020

from __future__ import unicode_literals

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from nnmware.apps.market.models import Basket, OrderItem
from nnmware.core.http import get_session_from_request
from nnmware.core.exceptions import MarketError
from nnmware.core.utils import send_template_mail


def get_basket(request):
    if not request.user.is_authenticated:
        session_key = get_session_from_request(request)
        return Basket.objects.filter(session_key=session_key)
    return Basket.objects.filter(user=request.user)


def send_new_order_seller(order):
    recipients = [settings.MARKET_MANAGER]
    mail_dict = {'order': order}
    subject = 'emails/neworder_admin_subject.txt'
    body = 'emails/neworder_admin_body.txt'
    send_template_mail(subject, body, mail_dict, recipients)


def send_new_order_buyer(order, recipients):
    mail_dict = {'order': order}
    subject = 'emails/neworder_client_subject.txt'
    body = 'emails/neworder_client_body.txt'
    send_template_mail(subject, body, mail_dict, recipients)


def make_order_from_basket(order, basket):
    # noinspection PyBroadException
    try:
        for item in basket:
            if settings.MARKET_CHECK_QUANTITY:
                if item.quantity > item.product.quantity:
                    raise MarketError
            order_item = OrderItem()
            order_item.order = order
            order_item.product_name = item.product.name
            order_item.product_origin = item.product
            order_item.product_url = item.product.get_absolute_url()
            order_item.amount = item.product.with_discount
            order_item.product_pn = item.product.market_pn
            order_item.quantity = item.quantity
            order_item.addon = item.addon
            order_item.save()
            if settings.MARKET_CHECK_QUANTITY:
                item.product.quantity -= item.quantity
                item.product.save()
        basket.delete()
        order_item = OrderItem()
        order_item.order = order
        order_item.product_name = order.delivery.name
        order_item.amount = order.delivery.amount
        order_item.quantity = 1
        order_item.addon = _('Delivery')
        order_item.save()
        return True
    except MarketError:
        return False
    except:
        return False
