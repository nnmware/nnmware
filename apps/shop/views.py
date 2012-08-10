# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from nnmware.apps.shop.form import EditProductForm
from nnmware.apps.shop.models import Product, ProductCategory, Basket
from nnmware.core.data import get_queryset_category
from nnmware.core.views import CurrentUserSuperuser, AttachedImagesMixin, AjaxFormMixin


class ShopCategory(ListView):
    template_name = 'shop/product_list.html'
    model = Product

    def get_queryset(self):
        result = get_queryset_category(self, Product, ProductCategory)
        return result

class ShopAllCategory(ListView):
    template_name = 'shop/product_list.html'
    model = Product

class BasketView(ListView):
    model = Basket
    template_name = 'shop/basket.html'

    def get_queryset(self):
        return Basket.objects.filter(user=self.request.user)

class EditProduct(CurrentUserSuperuser, AttachedImagesMixin, UpdateView, AjaxFormMixin):
    model = Product
    pk_url_kwarg = 'pk'
    form_class = EditProductForm
    template_name = "shop/edit_product.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        return super(EditProduct, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(EditProduct, self).get_context_data(**kwargs)
        context['title_line'] = _('edit form')
        return context

    def get_success_url(self):
        return '/'