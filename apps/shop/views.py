# -*- coding: utf-8 -*-
from __builtin__ import int, super, object
from datetime import date, timedelta
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Sum, Count
from django.db.models.query_utils import Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.list import ListView
from nnmware.apps.shop.form import EditProductForm, OrderStatusForm, OrderCommentForm, OrderTrackingForm
from nnmware.apps.shop.models import Product, ProductCategory, Basket, Order, ShopNews, Feedback, ShopArticle, ProductParameterValue, STATUS_PROCESS, STATUS_SENT
from nnmware.core.ajax import AjaxLazyAnswer
from nnmware.core.data import get_queryset_category
from nnmware.core.exceptions import AccessError
from nnmware.core.models import JComment
from nnmware.core.templatetags.core import basket, _get_basket
from nnmware.core.utils import send_template_mail, convert_to_date
from nnmware.core.views import CurrentUserSuperuser, AttachedImagesMixin, AjaxFormMixin
from django.contrib.contenttypes.models import ContentType

class CurrentUserOrderAccess(object):
    """ Generic update view that check request.user is author of object """
    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Order, pk=kwargs['pk'])
        if not request.user == obj.user and not request.user.is_superuser:
            raise Http404
        return super(CurrentUserOrderAccess, self).dispatch(request, *args, **kwargs)

class ShopCategory(ListView):
    template_name = 'shop/product_list.html'
    paginate_by = settings.PAGINATE_SHOP
    model = Product

    def get_queryset(self):
        result = get_queryset_category(self, Product, ProductCategory, active=True)
        return result

class ShopAllCategory(ListView):
    template_name = 'shop/product_list.html'
    model = Product
    paginate_by = settings.PAGINATE_SHOP

    def get_queryset(self):
        return Product.objects.active()

class SaleView(ListView):
    template_name = 'shop/sale_list.html'
    model = Product
    paginate_by = settings.PAGINATE_SHOP

    def get_queryset(self):
        return Product.objects.sale()


class ProductDetail(SingleObjectMixin, ListView):
    # For case-sensitive need UTF8_BIN collation in Slug_Field
    template_name = 'shop/product.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Product, pk=int(self.kwargs['pk']))

    def get_context_data(self, **kwargs):
        kwargs['object'] = self.object
        context = super(ProductDetail, self).get_context_data(**kwargs)
        object_type = ContentType.objects.get_for_model(self.object)
        param = ProductParameterValue.objects.filter(content_type__pk=object_type.id, object_id=self.object.id).order_by(
            'parameter__category','parameter__name')
        context['parameters'] = param
        return context

    def get_queryset(self):
        self.object = self.get_object()
        return JComment.public.get_tree(self.object)

class BasketView(TemplateView):
    template_name = 'shop/basket.html'

    def dispatch(self, request, *args, **kwargs):
        if _get_basket(request).count() < 1 :
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
    paginate_by = 20

    def get_queryset(self):
        q = self.request.GET.get('q') or None
        return Product.objects.filter( Q(name__icontains=q) | Q(name_en__icontains=q)).order_by('name')

class AddDeliveryAddressView(AjaxFormMixin, CreateView):
    pass

class OrdersView(ListView):
    template_name = 'shop/order_list.html'
    model = Order
    paginate_by = 25

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class AllOrdersView(ListView, CurrentUserSuperuser):
    template_name = 'shop/order_list.html'
    model = Order
    paginate_by = 25

    def get_queryset(self):
        return Order.objects.all()

class SumOrdersView(ListView, CurrentUserSuperuser):
    template_name = 'shop/order_list_sum.html'
    model = Order
    paginate_by = 25

    def get_queryset(self):
        return Order.objects.active().extra({'date_created' : "date(created_date)"}).values('date_created').annotate(orders=Count('id'))

class DateOrdersView(AllOrdersView):

    def get_queryset(self):
        on_date = convert_to_date(self.kwargs['on_date'])
        return Order.objects.filter(created_date__range=(on_date,on_date+timedelta(days=1)))

class OrderView(CurrentUserOrderAccess, DetailView):
    model = Order
    pk_url_kwarg = 'pk'
    template_name = 'shop/order.html'

class NewsListView(ListView):
    template_name = 'shop/news_list.html'
    model = ShopNews
    paginate_by = 10

class ArticleListView(ListView):
    template_name = 'shop/article_list.html'
    model = ShopArticle
    paginate_by = 10

class OrderStatusChange(CurrentUserSuperuser, UpdateView):
    model = Order
    slug_field = 'pk'
    form_class = OrderStatusForm
    template_name = "shop/order_status.html"

    def get_success_url(self):
        return reverse('order_view', args=[self.object.pk])

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        try:
            recipients = [self.request.user.email]
            mail_dict = {'order': self.object}
            if self.object.status == STATUS_PROCESS:
                subject = 'emails/status_process_subject.txt'
                body = 'emails/status_process_body.txt'
            if self.object.status == STATUS_SENT:
                subject = 'emails/status_sent_subject.txt'
                body = 'emails/status_sent_body.txt'
            send_template_mail(subject,body,mail_dict,recipients)
        except:
            pass
        return super(OrderStatusChange, self).form_valid(form)


class OrderTrackingChange(CurrentUserSuperuser, UpdateView):
    model = Order
    slug_field = 'pk'
    form_class = OrderTrackingForm
    template_name = "shop/order_tracking.html"

    def get_success_url(self):
        return reverse('order_view', args=[self.object.pk])


class OrderCommentChange(CurrentUserOrderAccess, UpdateView):
    model = Order
    slug_field = 'pk'
    form_class = OrderCommentForm
    template_name = "shop/order_comment.html"

    def get_success_url(self):
        return reverse('order_view', args=[self.object.pk])


class ProfileView(TemplateView):
    template_name = 'shop/profile.html'

class FeedbackView(CurrentUserSuperuser, DetailView):
    model = Feedback
    pk_url_kwarg = 'pk'
    template_name = 'shop/feedback.html'

