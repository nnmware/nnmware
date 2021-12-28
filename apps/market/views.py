# nnmware(c)2012-2020

from __future__ import unicode_literals
from datetime import timedelta

from django.conf import settings
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.db.models.query_utils import Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.list import ListView

from nnmware.apps.market.utils import get_basket
from nnmware.apps.market.form import EditProductForm, OrderStatusForm, OrderCommentForm, OrderTrackingForm
from nnmware.apps.market.models import Product, ProductCategory, Order, MarketNews, Feedback, MarketArticle, \
    ProductParameterValue, STATUS_PROCESS, STATUS_SENT, OrderItem
from nnmware.core.data import get_queryset_category
from nnmware.core.http import get_session_from_request
from nnmware.core.models import Nnmcomment
from nnmware.core.utils import send_template_mail, convert_to_date, setting
from nnmware.core.views import CurrentUserSuperuser, AttachedImagesMixin, AjaxFormMixin
from nnmware.apps.market.models import SpecialOffer, STATUS_WAIT, DeliveryAddress
from nnmware.apps.market.form import EditProductFurnitureForm, AnonymousUserOrderAddForm, RegisterUserOrderAddForm
from nnmware.apps.market.utils import make_order_from_basket
from nnmware.apps.market.utils import send_new_order_seller, send_new_order_buyer


class CurrentUserOrderAccess(object):
    """ Generic update view that check user is author of object """

    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Order, pk=kwargs['pk'])
        if not request.user.is_authenticated:
            if obj.session_key != get_session_from_request(request):
                raise Http404
        else:
            if not request.user == obj.user and not request.user.is_superuser:
                raise Http404
        return super(CurrentUserOrderAccess, self).dispatch(request, *args, **kwargs)


class MarketBaseView(ListView):
    template_name = 'market/product_list.html'
    paginate_by = setting('PAGINATE_BY', 20)
    model = Product

    def get_paginate_by(self, queryset):
        return self.request.session.get('paginator', self.paginate_by)


class MarketCategory(MarketBaseView):
    category = None
    sort = None

    def get_queryset(self):
        sort = self.request.GET.get('order') or None
        result, self.category = get_queryset_category(self, Product, ProductCategory, active=True)
        if sort is not None:
            self.sort = sort
            if sort == 'money_up':
                result = result.order_by('-amount')
            elif sort == 'money_down':
                result = result.order_by('amount')
            elif sort == 'date_up':
                result = result.order_by('-created_date')
            elif sort == 'date_down':
                result = result.order_by('created_date')
        return result

    def get_context_data(self, **kwargs):
        context = super(MarketCategory, self).get_context_data(**kwargs)
        context['category'] = self.category
        context['sort'] = self.sort
        return context


class MarketAllCategory(MarketBaseView):
    def get_queryset(self):
        return Product.objects.active()


class MarketSearch(MarketBaseView):
    template_name = 'market/product_search.html'
    q = None

    def get_queryset(self):
        q = self.request.GET.get('q') or None
        if q is not None:
            self.q = q
            return Product.objects.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q) |
                Q(teaser__icontains=q)).order_by('-created_date')
        return Product.objects.active()

    def get_context_data(self, **kwargs):
        context = super(MarketSearch, self).get_context_data(**kwargs)
        context['search'] = True
        if self.q is not None:
            context['search_string'] = self.q
        return context


class SaleView(MarketBaseView):
    template_name = 'market/sale_list.html'

    def get_queryset(self):
        return Product.objects.sale()


class ProductDetail(SingleObjectMixin, ListView):
    # For case-sensitive need UTF8_BIN collation in Slug_Field
    template_name = 'market/product.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Product, pk=int(self.kwargs['pk']))

    def get_context_data(self, **kwargs):
        kwargs['object'] = self.object
        context = super(ProductDetail, self).get_context_data(**kwargs)
        object_type = ContentType.objects.get_for_model(self.object)
        param = ProductParameterValue.objects.filter(content_type__pk=object_type.id, object_id=self.object.id)\
            .order_by('parameter__category', 'parameter__name')
        context['parameters'] = param
        return context

    def get_queryset(self):
        self.object = self.get_object()
        return Nnmcomment.public.get_tree(self.object)


class BasketView(TemplateView):
    template_name = 'market/basket.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.basket_.count() < 1:
            return HttpResponseRedirect('/')
        return super(BasketView, self).dispatch(request, *args, **kwargs)


class AllProductsView(ListView, CurrentUserSuperuser):
    paginate_by = 20
    model = Product
    template_name = 'market/adm_product_list.html'


class FeedbacksView(ListView, CurrentUserSuperuser):
    paginate_by = 20
    model = Feedback
    template_name = 'market/adm_feedback_list.html'


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
    template_name = "market/edit_product.html"

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


class EditProductFurniture(AjaxFormMixin, CurrentUserSuperuser, AttachedImagesMixin, UpdateView):
    model = Product
    pk_url_kwarg = 'pk'
    form_class = EditProductFurnitureForm
    template_name = "market/edit_product.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        return super(EditProductFurniture, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(EditProductFurniture, self).get_context_data(**kwargs)
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
    template_name = 'market/product_list.html'
    model = Product
    paginate_by = 20

    def get_queryset(self):
        q = self.request.GET.get('q') or None
        return Product.objects.filter(Q(name__icontains=q) | Q(name_en__icontains=q)).order_by('name')


class AddDeliveryAddressView(AjaxFormMixin, CreateView):
    pass


class OrdersView(ListView):
    template_name = 'market/order_list.html'
    model = Order
    paginate_by = 60

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class BaseOrdersView(ListView, CurrentUserSuperuser):
    template_name = 'market/order_list.html'
    model = Order
    paginate_by = 60


class AllOrdersView(BaseOrdersView):
    def get_queryset(self):
        return Order.objects.all()


class SumOrdersView(BaseOrdersView):
    template_name = 'market/order_list_sum.html'

    def get_queryset(self):
        return Order.objects.active().extra({'date_created': "date(created_date)"}).values('date_created').annotate(
            orders=Count('id'))


class PieProductListView(ListView, CurrentUserSuperuser):
    template_name = 'market/pie.html'

    def get_queryset(self):
        active = Order.objects.active()
        products = OrderItem.objects.filter(order__in=active).values_list('product_origin__pk', flat=True)
        result = Product.objects.filter(pk__in=products)
        return result


class DateOrdersView(AllOrdersView):
    def get_queryset(self):
        on_date = convert_to_date(self.kwargs['on_date'])
        return Order.objects.filter(created_date__range=(on_date, on_date + timedelta(days=1)))


class OrderView(CurrentUserOrderAccess, DetailView):
    model = Order
    pk_url_kwarg = 'pk'
    template_name = 'market/order.html'


class OrderCompleteView(CurrentUserOrderAccess, DetailView):
    model = Order
    pk_url_kwarg = 'pk'
    template_name = 'market/order_complete.html'


class NewsListView(ListView):
    template_name = 'market/news_list.html'
    model = MarketNews
    paginate_by = 10


class ArticleListView(ListView):
    template_name = 'market/article_list.html'
    model = MarketArticle
    paginate_by = 10


class OrderStatusChange(CurrentUserSuperuser, UpdateView):
    model = Order
    slug_field = 'pk'
    form_class = OrderStatusForm
    template_name = "market/order_status.html"

    def get_success_url(self):
        return reverse('order_view', args=[self.object.pk])

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        # noinspection PyBroadException
        try:
            recipients = [self.request.user.email]
            mail_dict = {'order': self.object}
            subject = body = ''
            if self.object.status == STATUS_PROCESS:
                subject = 'emails/status_process_subject.txt'
                body = 'emails/status_process_body.txt'
            if self.object.status == STATUS_SENT:
                subject = 'emails/status_sent_subject.txt'
                body = 'emails/status_sent_body.txt'
            send_template_mail(subject, body, mail_dict, recipients)
        except:
            pass
        return super(OrderStatusChange, self).form_valid(form)


class OrderTrackingChange(CurrentUserSuperuser, UpdateView):
    model = Order
    slug_field = 'pk'
    form_class = OrderTrackingForm
    template_name = "market/order_tracking.html"

    def get_success_url(self):
        return reverse('order_view', args=[self.object.pk])


class OrderCommentChange(CurrentUserOrderAccess, UpdateView):
    model = Order
    slug_field = 'pk'
    form_class = OrderCommentForm
    template_name = "market/order_comment.html"

    def get_success_url(self):
        return reverse('order_view', args=[self.object.pk])


class ProfileView(TemplateView):
    template_name = 'market/profile.html'


class FeedbackView(CurrentUserSuperuser, DetailView):
    model = Feedback
    pk_url_kwarg = 'pk'
    template_name = 'market/feedback.html'


class SpecialOfferView(DetailView):
    model = SpecialOffer
    template_name = 'market/offer.html'


class AnonymousUserAddOrderView(AjaxFormMixin, CreateView):
    model = Order
    form_class = AnonymousUserOrderAddForm
    template_name = 'market/quick_order.html'

    def form_valid(self, form):
        if not self.request.user.is_authenticated and not settings.MARKET_ANONYMOUS_ORDERS:
            return super(AnonymousUserAddOrderView, self).form_invalid(form)
        basket = get_basket(self.request)
        if basket.count() < 1:
            return super(AnonymousUserAddOrderView, self).form_invalid(form)
        self.object = form.save(commit=False)
        self.object.ip = self.request.META['REMOTE_ADDR']
        self.object.user_agent = self.request.META['HTTP_USER_AGENT']
        self.object.status = STATUS_WAIT
        self.object.lite = True
        self.object.session_key = get_session_from_request(self.request)
        self.object.save()
        success_add_items = make_order_from_basket(self.object, basket)
        if success_add_items is not True:
            self.object.delete()
            return super(AnonymousUserAddOrderView, self).form_invalid(form)
        send_new_order_seller(self.object)
        send_new_order_buyer(self.object, [self.object.email])
        return super(AnonymousUserAddOrderView, self).form_valid(form)

    def get_success_url(self):
        return self.object.get_complete_url()


class RegisterUserAddOrderView(AjaxFormMixin, CreateView):
    model = Order
    template_name = 'market/new_order.html'
    form_class = RegisterUserOrderAddForm

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            return super(RegisterUserAddOrderView, self).form_invalid(form)
        basket = get_basket(self.request)
        if basket.count() < 1:
            return super(RegisterUserAddOrderView, self).form_invalid(form)
        addr = self.request.POST.get('addr')
        address = DeliveryAddress.objects.get(user=self.request.user, pk=int(addr))
        self.object = form.save(commit=False)
        self.object.address = str(address)
        self.object.ip = self.request.META['REMOTE_ADDR']
        self.object.user_agent = self.request.META['HTTP_USER_AGENT']
        self.object.status = STATUS_WAIT
        self.object.lite = False
        self.object.first_name = address.first_name
        self.object.middle_name = address.middle_name
        self.object.last_name = address.last_name
        self.object.phone = address.phone
        self.object.email = self.request.user.email
        self.object.user = self.request.user
        self.object.save()
        success_add_items = make_order_from_basket(self.object, basket)
        if success_add_items is not True:
            self.object.delete()
            return super(RegisterUserAddOrderView, self).form_invalid(form)
        send_new_order_seller(self.object)
        send_new_order_buyer(self.object, [self.request.user.email])
        return super(RegisterUserAddOrderView, self).form_valid(form)

    def get_success_url(self):
        return self.object.get_complete_url()
