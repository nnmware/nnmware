# -*- coding: utf-8 -*-
from django.conf import settings
from nnmware.apps.shop.models import Basket, OrderItem
from nnmware.core.http import get_session_from_request
from nnmware.core.exceptions import ShopError

def get_basket(request):
    if not request.user.is_authenticated():
        session_key = get_session_from_request(request)
        return Basket.objects.filter(session_key=session_key)
    return Basket.objects.filter(user=request.user)

def make_order_from_basket(order, basket):
    if 1>0: #try:
        for item in basket:
            if settings.SHOP_CHECK_QUANTITY:
                if item.quantity > item.product.quantity:
                    raise ShopError
            order_item = OrderItem()
            order_item.order = order
            order_item.product_name = item.product.name
            order_item.product_origin = item.product
            order_item.product_url = item.product.get_absolute_url
            order_item.amount = item.product.with_discount
            order_item.product_pn = item.product.shop_pn
            order_item.quantity = item.quantity
            order_item.addon = item.addon
            order_item.save()
            if settings.SHOP_CHECK_QUANTITY:
                item.product.quantity -= item.quantity
                item.product.save()
        basket.delete()
        return True
#    except ShopError:
#        return False
#    except:
#        return False
