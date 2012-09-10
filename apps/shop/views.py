# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.list import ListView
from nnmware.apps.shop.form import EditProductForm, OrderStatusForm
from nnmware.apps.shop.models import Product, ProductCategory, Basket, Order, ShopNews, Feedback
from nnmware.core.ajax import AjaxLazyAnswer
from nnmware.core.data import get_queryset_category
from nnmware.core.exceptions import AccessError
from nnmware.core.models import JComment
from nnmware.core.templatetags.core import basket
from nnmware.core.views import CurrentUserSuperuser, AttachedImagesMixin, AjaxFormMixin


class ShopCategory(ListView):
    template_name = 'shop/product_list.html'
    paginate_by = 21
    model = Product

    def get_queryset(self):
        result = get_queryset_category(self, Product, ProductCategory, active=True)
        return result

class ShopAllCategory(ListView):
    template_name = 'shop/product_list.html'
    model = Product
    paginate_by = 21

    def get_queryset(self):
        return Product.objects.active()

class ProductDetail(SingleObjectMixin, ListView):
    # For case-sensitive need UTF8_BIN collation in Slug_Field
    paginate_by = 20
    template_name = 'shop/product.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Product, pk=int(self.kwargs['pk']))

    def get_context_data(self, **kwargs):
        kwargs['object'] = self.object
        context = super(ProductDetail, self).get_context_data(**kwargs)
        return context

    def get_queryset(self):
        self.object = self.get_object()
        return JComment.public.get_tree(self.object)

class BasketView(View):
    template_name = 'shop/basket.html'

    def dispatch(self, request, *args, **kwargs):
        if Basket.objects.filter(user=request.user).count() < 1 :
            return HttpResponseRedirect('/')
        return super(BasketView, self).dispatch(request, *args, **kwargs)

class AllProductsView(ListView,CurrentUserSuperuser):
    paginate_by = 20
    model = Product
    template_name = 'shop/adm_product_list.html'

class FeedbacksView(ListView,CurrentUserSuperuser):
    paginate_by = 20
    model = Feedback
    template_name = 'shop/adm_feedback_list.html'


class AvailProductsView(AllProductsView):

    def get_queryset(self):
        return Product.objects.filter(avail=True)

class NotAvailProductsView(AllProductsView):

    def get_queryset(self):
        return Product.objects.filter(avail=False)

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
        return self.object.get_absolute_url()

def add_product(request):
    # Link used when admin add product
   if not request.user.is_superuser:
        raise Http404
   p = Product()
   p.name = _('New product')
   p.avail = False
   p.save()
   return HttpResponseRedirect(reverse("edit_product", args=[p.pk]))

class SearchView(ListView):
    template_name = 'shop/product_list.html'
    model = Product
    paginate_by = 10

    def get_queryset(self):
        q = self.request.GET.get('q') or None
        return Product.objects.filter( Q(name__icontains=q) | Q(name_en__icontains=q)).order_by('name')

class AddDeliveryAddressView(AjaxFormMixin, CreateView):
    pass

class OrdersView(ListView):
    template_name = 'shop/order_list.html'
    model = Order
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class AllOrdersView(ListView, CurrentUserSuperuser):
    template_name = 'shop/order_list.html'
    model = Order
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.all()

class OrderView(DetailView):
    model = Order
    pk_url_kwarg = 'pk'
    template_name = 'shop/order.html'

class NewsListView(ListView):
    template_name = 'shop/news_list.html'
    model = ShopNews
    paginate_by = 10

class OrderStatusChange(CurrentUserSuperuser, UpdateView):
    model = Order
    slug_field = 'pk'
    form_class = OrderStatusForm
    template_name = "shop/order_status.html"

    def get_success_url(self):
        return reverse('order_view', args=[self.object.pk])

class ProfileView(TemplateView):
    template_name = 'shop/profile.html'

class FeedbackView(DetailView):
    model = Feedback
    pk_url_kwarg = 'pk'
    template_name = 'shop/feedback.html'
