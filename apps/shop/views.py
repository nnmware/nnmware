# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from nnmware.apps.shop.form import EditProductForm
from nnmware.apps.shop.models import Product, ProductCategory, Basket
from nnmware.core.data import get_queryset_category
from nnmware.core.models import JComment
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

class ProductDetail(SingleObjectMixin, ListView):
    # For case-sensitive need UTF8_BIN collation in Slug_Field
    paginate_by = 20
    template_name = 'shop/product.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Product, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        kwargs['object'] = self.object
        context = super(ProductDetail, self).get_context_data(**kwargs)
        return context

    def get_queryset(self):
        self.object = self.get_object()
        return JComment.public.get_tree(self.object)

class BasketView(ListView):
    model = Basket
    template_name = 'shop/basket.html'

    def get_queryset(self):
        return Basket.objects.filter(user=self.request.user)

class EditProduct(AjaxFormMixin, CurrentUserSuperuser, AttachedImagesMixin, UpdateView):
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
        return self.object.get_absolute_url

