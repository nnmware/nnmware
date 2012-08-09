# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.views.generic.list import ListView
from nnmware.apps.shop.models import Product, ProductCategory
from nnmware.core.data import get_queryset_category



class ShopCategory(ListView):
    template_name = 'shop/product_list.html'
    model = Product

    def get_queryset(self):
        result = get_queryset_category(self, Product, ProductCategory)
        return result

