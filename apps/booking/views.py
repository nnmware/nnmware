# -*- coding: utf-8 -*-

from datetime import date, timedelta, datetime
from decimal import Decimal
from hashlib import sha1
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.mail import mail_managers
from django.db.models import Count, Sum, Q, Max, F
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic.base import View, TemplateView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import FormView, UpdateView, CreateView
from django.views.generic.list import ListView
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.booking.models import Hotel, Room, RoomOption, SettlementVariant, Availability, PlacePrice, \
    STATUS_ACCEPTED, HotelOption
from nnmware.apps.booking.forms import *
from nnmware.apps.booking.utils import guests_from_request, booking_new_hotel_mail, request_add_hotel_mail
from nnmware.core.ajax import AjaxLazyAnswer
from nnmware.core.config import CURRENCY
from nnmware.core.http import get_session_from_request
from nnmware.core.views import AttachedImagesMixin, AttachedFilesMixin, AjaxFormMixin, \
    CurrentUserSuperuser, RedirectHttpView, RedirectHttpsView
from nnmware.apps.money.models import Bill, Currency
from nnmware.core.utils import convert_to_date, daterange
from nnmware.core.financial import convert_from_client_currency
from nnmware.core.financial import is_luhn_valid
from nnmware.apps.booking.utils import booking_new_client_mail
from nnmware.apps.address.models import City
from nnmware.core.decorators import ssl_required
from django.views.decorators.cache import never_cache
from nnmware.core.views import AjaxViewMixin


class CurrentUserHotelAdmin(object):
    """ Generic update view that check request.user is author of object """

    @method_decorator(ssl_required)
    @method_decorator(ensure_csrf_cookie)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Hotel.objects.select_related(), city__slug=kwargs['city'], slug=kwargs['slug'])
        if not request.user in obj.admins.all() and not request.user.is_superuser:
            raise Http404
        return super(CurrentUserHotelAdmin, self).dispatch(request, *args, **kwargs)


class CurrentUserRoomAdmin(object):
    """ Generic update view that check request.user is author of object """

    @method_decorator(ssl_required)
    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Room.objects.select_related(), pk=kwargs['pk'])
        if not request.user in obj.hotel.admins.all() and not request.user.is_superuser:
            raise Http404
        return super(CurrentUserRoomAdmin, self).dispatch(request, *args, **kwargs)


class CurrentUserHotelBillAccess(object):
    """ Generic update view that check request.user may view bills of hotel """

    @method_decorator(ssl_required)
    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Bill.objects.select_related(), pk=kwargs['pk'])
        if not request.user in obj.target.admins.all() and not request.user.is_superuser:
            raise Http404
        return super(CurrentUserHotelBillAccess, self).dispatch(request, *args, **kwargs)


class CurrentUserHotelBookingAccess(object):
    """ Generic update view that check request.user may view bookings of hotel """

    @method_decorator(ssl_required)
    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Booking.objects.select_related(), uuid=kwargs['slug'])
        if not request.user in obj.hotel.admins.all() and not request.user.is_superuser:
            raise Http404
        return super(CurrentUserHotelBookingAccess, self).dispatch(request, *args, **kwargs)


class CurrentUserBookingAccess(object):
    """ Generic update view that check request.user may view bookings of hotel """

    @method_decorator(ssl_required)
    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Booking.objects.select_related(), uuid=kwargs['slug'])
        if obj.user:
            if (request.user != obj.user) and not request.user.is_superuser:
                raise Http404
        return super(CurrentUserBookingAccess, self).dispatch(request, *args, **kwargs)


class CurrentUserCabinetAccess(object):
    @method_decorator(ssl_required)
    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(get_user_model(), username=kwargs['username'])
        if not (request.user == obj) and not request.user.is_superuser:
            raise Http404
        return super(CurrentUserCabinetAccess, self).dispatch(request, *args, **kwargs)


def hotel_order(arr, order, sort):
    ui_order = '?'
    if order in ['name', 'starcount', 'current_amount', 'point'] and sort in ['asc', 'desc']:
        arr['tab'] = order
        if sort == 'asc':
            ui_order = order
            arr['css_' + order] = 'asc'
            arr['order_' + order] = 'desc'
        else:
            ui_order = '-' + order
            arr['css_' + order] = 'desc'
            arr['order_' + order] = 'asc'
    return arr, ui_order


class HotelList(AjaxViewMixin, RedirectHttpView, ListView):
    paginate_by = 20
    model = Hotel
    template_name = "hotels/list.html"
    search = 0

    def post(self, request, *args, **kwargs):
        return super(HotelList, self).get(request, *args, **kwargs)

    def get_queryset(self):
        key = sha1('%s' % (self.request.get_full_path(),)).hexdigest()
        result = []
        searched_date = False
        self.search_data = dict()
        order = self.request.GET.get('order') or None
        sort = self.request.GET.get('sort') or None
        notknowndates = self.request.GET.get('notknowndates') or None
        guests = guests_from_request(self.request)
        f_date = self.request.GET.get('from') or None
        t_date = self.request.GET.get('to') or None
        amount_min = self.request.REQUEST.get('amount_min') or None
        amount_max = self.request.REQUEST.get('amount_max') or None
        options = self.request.REQUEST.getlist('options') or None
        stars = self.request.REQUEST.getlist('stars') or None
        self.tab = {'css_name': 'asc', 'css_starcount': 'desc', 'css_current_amount': 'desc', 'css_point': 'desc',
                    'order_name': 'desc', 'order_starcount': 'desc', 'order_current_amount': 'desc',
                    'order_point': 'desc', 'tab': 'name'}
        try:
            self.city = City.objects.get(slug=self.kwargs['slug'])
        except:
            self.city = None
        if self.city:
            if f_date and t_date:
                try:
                    from_date = convert_to_date(f_date)
                    to_date = convert_to_date(t_date)
                    if from_date > to_date:
                        self.search_data = {'from_date': t_date, 'to_date': f_date, 'guests': guests}
                        from_date, to_date = to_date, from_date
                    else:
                        self.search_data = {'from_date': f_date, 'to_date': t_date, 'guests': guests}
                    self.search_data['city'] = self.city
                    if stars:
                        self.search_data['stars'] = stars
                    if options:
                        self.search_data['options'] = options
                    if from_date < datetime.now():
                        self.result_count = 0
                        result = []
                        return result
                    searched_date = True
                except:
                    pass
                finally:
                    self.search = 1
            elif notknowndates:
                self.search = 1
        self.result_count = None
        data_key = None
        if self.request.is_ajax():
            self.template_name = "hotels/list_ajax.html"
            path = self.request.REQUEST.get('path') or None
            if path:
                key = sha1('%s' % (path,)).hexdigest()
                data_key = cache.get(key)
        else:
            data_key = cache.get(key)
        if not data_key:
            if self.city:
                search_hotel = Hotel.objects.select_related().filter(city=self.city)  # .exclude(payment_method=None)
            else:
                search_hotel = Hotel.objects.select_related().all()
            if searched_date:
                result = []
                # Find all rooms pk for this guest count
                rooms_list = SettlementVariant.objects.filter(enabled=True, settlement__gte=guests).\
                    values_list('room__id', flat=True).distinct()
                need_days = (to_date - from_date).days
                date_period = (from_date, to_date-timedelta(days=1))
                searched_hotels_list = Availability.objects.filter(room__pk__in=rooms_list, date__in=date_period,
                    min_days__lte=need_days, placecount__gt=0).annotate(num_days=Sum('room')).\
                    filter(num_days__gte=need_days).order_by('room__hotel').values_list('room__hotel__pk',
                                                                                        flat=True).distinct()
                search_hotel = search_hotel.filter(pk__in=searched_hotels_list)
            result = search_hotel
            hotels_pk_list = result.values_list('pk', flat=True).distinct()
            cache.set(key, hotels_pk_list, 300)
        else:
            search_hotel = Hotel.objects.filter(pk__in=data_key)
        if amount_max and amount_min:
            self.search_data['amount'] = [amount_min, amount_max]
            if searched_date:
                hotels_with_amount = PlacePrice.objects.filter(date=from_date,
                    amount__range=(amount_min, amount_max)).values_list('settlement__room__hotel__pk',
                    flat=True).distinct()
            else:
                hotels_with_amount = PlacePrice.objects.filter(date=datetime.today(),
                    amount__range=(amount_min, amount_max)).values_list('settlement__room__hotel__pk',
                    flat=True).distinct()
            search_hotel = search_hotel.filter(Q(pk__in=hotels_with_amount) | Q(work_on_request=True))
        if options:
            for option in options:
                search_hotel = search_hotel.filter(option=option)
        if stars:
            search_hotel = search_hotel.filter(starcount__in=stars)
        if order:
            self.tab, ui_order = hotel_order(self.tab, order, sort)
            search_hotel = search_hotel.order_by(ui_order)
        if not f_date and not t_date:
            self.search_data = {'from_date': (datetime.today() + timedelta(days=1)).strftime("%d.%m.%Y"),
                                'to_date': (datetime.today() + timedelta(days=2)).strftime("%d.%m.%Y"), 'guests': 1}
        result = search_hotel.annotate(Count('review'))
        if result:
            self.result_count = result.count()
        else:
            self.result_count = 0
        self.payload['result_count'] = self.result_count
        return result

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(HotelList, self).get_context_data(**kwargs)
        context['title_line'] = _('list of hotels')
        context['tab'] = self.tab
        context['path'] = self.request.get_full_path()
        if self.search:
            context['search'] = self.search
        else:
            context['country'] = 1
        if self.city:
            context['city'] = self.city
        context['search_data'] = self.search_data
        context['hotels_in_city'] = self.result_count
        return context


class HotelAdminList(ListView):
    model = Hotel
    paginate_by = 50
    template_name = "usercabinet/list.html"

    def get_queryset(self):
        if self.request.user.is_authenticated():
            if self.request.user.is_superuser:
                result = Hotel.objects.all()
            else:
                result = Hotel.objects.filter(admins=self.request.user)
            return result.order_by('city__name', 'name')
        raise Http404

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(HotelAdminList, self).get_context_data(**kwargs)
        context['title_line'] = _('list of hotels')
        context['tab'] = _('admin of hotels')
        return context


class HotelPathMixin(object):
    def get_object(self, queryset=None):
        return get_object_or_404(Hotel.objects.select_related(), city__slug=self.kwargs['city'],
            slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super(HotelPathMixin, self).get_context_data(**kwargs)
        context['hotel'] = self.object
        return context


class HotelDetail(AjaxViewMixin, HotelPathMixin, AttachedImagesMixin, DetailView):
    model = Hotel
    template_name = "hotels/detail.html"

    def post(self, request, *args, **kwargs):
        return super(HotelDetail, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        f_date = self.request.GET.get('from') or None
        t_date = self.request.GET.get('to') or None
        guests = guests_from_request(self.request)
        options = self.request.REQUEST.getlist('options') or None
        # Call the base implementation first to get a context
        context = super(HotelDetail, self).get_context_data(**kwargs)
        context['tab'] = 'description'
        context['city'] = self.object.city
        context['hotels_in_city'] = Hotel.objects.filter(city=self.object.city).count()
        context['title_line'] = self.object.get_name
        context['hotel_options'] = self.object.option.select_related().order_by('category', 'order_in_list', 'name')
        context['search_url'] = self.object.get_absolute_url()
        if self.request.is_ajax():
            self.template_name = "hotels/rooms_ajax.html"
        if f_date and t_date and guests:
            from_date = convert_to_date(f_date)
            to_date = convert_to_date(t_date)
            if from_date > to_date:
                from_date, to_date = to_date, from_date
                f_date, t_date = t_date, f_date
            need_days = (to_date - from_date).days
            if from_date < datetime.now():
                rooms = []
            else:
                # Find all rooms pk for this guest count
                rooms_list = SettlementVariant.objects.filter(enabled=True, settlement__gte=guests,
                    room__hotel=self.object).values_list('room__id', flat=True).distinct()
                date_period = (from_date, to_date-timedelta(days=1))
                searched_room_list = Availability.objects.filter(room__pk__in=rooms_list, date__range=date_period,
                    min_days__lte=need_days, placecount__gt=0).annotate(num_days=Sum('room')).\
                    filter(num_days__gte=need_days).order_by('room').values_list('room__pk', flat=True).distinct()
                room_with_amount_list = PlacePrice.objects.filter(settlement__room__pk__in=rooms_list,
                    date__range=date_period, amount__gte=0).annotate(num_days=Sum('settlement__room')).\
                    filter(num_days__gte=need_days).order_by('settlement__room').values_list('settlement__room__pk',
                                                                                             flat=True).distinct()
                rooms = Room.objects.select_related().filter(pk__in=searched_room_list).\
                    filter(pk__in=room_with_amount_list)
            search_data = {'from_date': f_date, 'to_date': t_date, 'guests': guests, 'city': self.object.city}
            context['search'] = 1
            context['need_days'] = need_days
        else:
            search_data = {'from_date': (datetime.today() + timedelta(days=1)).strftime("%d.%m.%Y"),
                                'to_date': (datetime.today() + timedelta(days=2)).strftime("%d.%m.%Y"), 'guests': 1}
            rooms = self.object.room_set.all()
        if options:
            for option in options:
                rooms = rooms.filter(option=option)
        context['rooms'] = rooms
        if rooms:
            self.payload['result_count'] = rooms.count()
        else:
            self.payload['result_count'] = 0
        context['search_data'] = search_data
        return context


class HotelLocation(RedirectHttpView, HotelPathMixin, DetailView):
    slug_field = 'slug'
    template_name = "hotels/location.html"

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(HotelLocation, self).get_context_data(**kwargs)
        context['city'] = self.object.city
        context['hotels_in_city'] = Hotel.objects.filter(city=self.object.city).count()
        context['tourism_list'] = self.object.tourism_places()
        context['title_line'] = self.object.get_name
        context['tab'] = 'location'
        return context


class HotelReviews(HotelPathMixin, SingleObjectMixin, ListView):
    paginate_by = 5
    slug_field = 'slug'
    template_name = "hotels/reviews.html"

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        kwargs['object'] = self.object
        context = super(HotelReviews, self).get_context_data(**kwargs)
        context['city'] = self.object.city
        context['hotels_in_city'] = Hotel.objects.filter(city=self.object.city).count()
        context['tab'] = 'reviews'
        context['title_line'] = self.object.get_name
        return context

    def get_queryset(self):
        self.object = self.get_object()
        return self.object.review_set.all()


class RoomDetail(AttachedImagesMixin, DetailView):
    model = Room
    template_name = 'hotels/room.html'

    def get_context_data(self, **kwargs):
        f_date = self.request.GET.get('from') or None
        t_date = self.request.GET.get('to') or None
        guests = guests_from_request(self.request)
        context = super(RoomDetail, self).get_context_data(**kwargs)
        if self.object.hotel is not None:
            context['city'] = self.object.hotel.city
            context['title_line'] = self.object.hotel.get_name
            context['hotels_in_city'] = Hotel.objects.filter(city=self.object.hotel.city).count()
            context['search_url'] = self.object.hotel.get_absolute_url()
            context['hotel'] = self.object.hotel
        context['tab'] = 'description'
        context['room_options'] = self.object.option.select_related().order_by('category', 'order_in_list', 'name')
        if f_date and t_date and guests:
            from_date = convert_to_date(f_date)
            to_date = convert_to_date(t_date)
            if from_date > to_date:
                f_date, t_date = t_date, f_date
            search_data = {'from_date': f_date, 'to_date': t_date, 'guests': guests, 'city': self.object.hotel.city}
            context['search'] = 1
        else:
            search_data = {'from_date': (datetime.today() + timedelta(days=1)).strftime("%d.%m.%Y"),
                'to_date': (datetime.today() + timedelta(days=2)).strftime("%d.%m.%Y"), 'guests': 1}
        context['search_data'] = search_data
        return context


class CabinetInfo(HotelPathMixin, CurrentUserHotelAdmin, AttachedImagesMixin, UpdateView):
    model = Hotel
    form_class = CabinetInfoForm
    template_name = "cabinet/info.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CabinetInfo, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.city).count()
        context['options_list'] = HotelOption.objects.select_related().order_by('category', 'order_in_list', 'name')
        context['tab'] = 'common'
        context['title_line'] = _('private cabinet')
        return context

    def get_success_url(self):
        return reverse('cabinet_info', args=[self.object.city.slug, self.object.slug])


class CabinetTerms(HotelPathMixin, CurrentUserHotelAdmin, UpdateView):
    model = Hotel
    form_class = CabinetTermsForm
    template_name = "cabinet/terms.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CabinetTerms, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.city).count()
        context['all_payment_methods'] = PaymentMethod.objects.order_by('name')
        context['tab'] = 'terms'
        context['title_line'] = _('private cabinet')
        return context

    def get_success_url(self):
        return reverse('cabinet_terms', args=[self.object.city.slug, self.object.slug])


class CabinetRooms(HotelPathMixin, CurrentUserHotelAdmin, CreateView):
    model = Room
    form_class = CabinetRoomForm
    template_name = "cabinet/rooms.html"

    def form_valid(self, form):
        hotel = get_object_or_404(Hotel, city__slug=self.kwargs['city'], slug=self.kwargs['slug'])
        self.object = form.save(commit=False)
        self.object.hotel = hotel
        self.object.save()
        return super(CabinetRooms, self).form_valid(form)

    def get_context_data(self, **kwargs):
        hotel = get_object_or_404(Hotel.objects.select_related(), city__slug=self.kwargs['city'],
                                  slug=self.kwargs['slug'])
        # Call the base implementation first to get a context
        context = super(CabinetRooms, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=hotel.city).count()
        context['options_list'] = RoomOption.objects.select_related().order_by('category', 'order_in_list', 'name')
        context['tab'] = 'rooms'
        context['hotel'] = hotel
        context['title_line'] = _('private cabinet')
        return context

    def get_success_url(self):
        return reverse('cabinet_room', args=[self.object.hotel.city.slug, self.object.hotel.slug, self.object.pk])


class CabinetEditRoom(CurrentUserRoomAdmin, AttachedImagesMixin, UpdateView):
    model = Room
    pk_url_kwarg = 'pk'
    form_class = CabinetRoomForm
    template_name = "cabinet/room.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CabinetEditRoom, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.hotel.city).count()
        context['options_list'] = RoomOption.objects.select_related().order_by('category', 'order_in_list', 'name')
        context['tab'] = 'rooms'
        context['hotel'] = self.object.hotel
        context['title_line'] = _('private cabinet')
        return context

    def get_success_url(self):
        return reverse('cabinet_rooms', args=[self.object.hotel.city.slug, self.object.hotel.slug])

    def form_valid(self, form):
        variants = self.request.POST.getlist('settlement')
        self.object.places = max(variants)
        self.object.save()
        SettlementVariant.objects.filter(room=self.object).update(enabled=False)
        for variant in variants:
            try:
                settlement = SettlementVariant.objects.get(room=self.object, settlement=variant)
                settlement.enabled = True
                settlement.save()
            except:
                SettlementVariant(room=self.object, settlement=variant, enabled=True).save()
        return super(CabinetEditRoom, self).form_valid(form)


class CabinetRates(HotelPathMixin, CurrentUserHotelAdmin, DetailView):
    model = Hotel
    template_name = "cabinet/rates.html"

    def get_context_data(self, **kwargs):
        f_date = self.request.GET.get('from') or None
        t_date = self.request.GET.get('to') or None
        days_of_week = self.request.GET.getlist('days_of_week') or None
        # Call the base implementation first to get a context
        context = super(CabinetRates, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.city).count()
        context['tab'] = 'rates'
        context['hotel'] = self.object
        context['title_line'] = _('private cabinet')
        if 'room' in self.kwargs.keys():
            context['room_id'] = int(self.kwargs['room'])
        else:
            try:
                context['room_id'] = Room.objects.filter(hotel=self.object)[0].id
            except IndexError:
                pass
        if f_date and t_date:
            from_date = convert_to_date(f_date)
            to_date = convert_to_date(t_date)
            if from_date > to_date:
                from_date, to_date = to_date, from_date
            if (to_date - from_date).days > 365:
                to_date = from_date + timedelta(days=365)
            date_gen = daterange(from_date, to_date + timedelta(days=1))
        else:
            from_date = datetime.now()
            to_date = from_date + timedelta(days=14)
            date_gen = daterange(from_date, to_date)
            f_date = datetime.strftime(from_date, "%d.%m.%Y")
            t_date = datetime.strftime(to_date, "%d.%m.%Y")
        if from_date < to_date:
            context['search_dates'] = {'from_date': f_date, 'to_date': t_date}
        else:
            context['search_dates'] = {'from_date': t_date, 'to_date': f_date}
        date_period = []
        for i in date_gen:
            if days_of_week:
                if str(i.isoweekday()) in days_of_week:
                    date_period.append(i)
            else:
                date_period.append(i)
        context['dates'] = date_period
        context['days_of_week'] = days_of_week
        return context


class CabinetDiscount(CabinetRates):
    def get_context_data(self, **kwargs):
        context = super(CabinetDiscount, self).get_context_data(**kwargs)
        context['discount'] = True
        context['tab'] = 'discounts'
        return context


class CabinetBillEdit(CurrentUserHotelBillAccess, AttachedFilesMixin, UpdateView):
    model = Bill
    form_class = CabinetEditBillForm
    template_name = "cabinet/bill_edit.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CabinetBillEdit, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.target.city).count()
        context['tab'] = 'reports'
        context['hotel'] = self.object.target
        context['title_line'] = _('private cabinet')
        return context

    def get_success_url(self):
        return reverse('cabinet_bills', args=[self.object.target.city.slug, self.object.target.slug])


class CabinetBookings(HotelPathMixin, CurrentUserHotelAdmin, SingleObjectMixin, ListView):
    paginate_by = 20
    template_name = "cabinet/bookings.html"
    search_dates = dict()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        kwargs['object'] = self.object
        context = super(CabinetBookings, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.city).count()
        context['tab'] = 'reports'
        context['hotel'] = self.object
        context['title_line'] = _('bookings')
        context['search_dates'] = self.search_dates
        return context

    def get_queryset(self):
        self.object = self.get_object()
        f_date = self.request.GET.get('from') or None
        t_date = self.request.GET.get('to') or None
        if f_date is not None and t_date is not None:
            from_date = convert_to_date(f_date)
            to_date = convert_to_date(t_date)
            if from_date > to_date:
                from_date, to_date = to_date, from_date
            if (to_date - from_date).days > 365:
                to_date = from_date + timedelta(days=365)
        else:
            from_date = datetime.now()
            to_date = from_date + timedelta(days=14)
            f_date = datetime.strftime(from_date, "%d.%m.%Y")
            t_date = datetime.strftime(to_date, "%d.%m.%Y")
        if from_date < to_date:
            self.search_dates = {'from_date': f_date, 'to_date': t_date}
        else:
            from_date, to_date = to_date, from_date
            self.search_dates = {'from_date': t_date, 'to_date': f_date}
        return Booking.objects.filter(hotel=self.object, date__range=(from_date, to_date))


class CabinetBills(HotelPathMixin, CurrentUserHotelAdmin, SingleObjectMixin, ListView):
    template_name = "cabinet/bills.html"
    search_dates = dict()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        kwargs['object'] = self.object
        context = super(CabinetBills, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.city).count()
        context['tab'] = 'reports'
        context['hotel'] = self.object
        context['title_line'] = _('bills')
        context['search_dates'] = self.search_dates
        return context

    def get_queryset(self):
        self.object = self.get_object()
        f_date = self.request.GET.get('from') or None
        t_date = self.request.GET.get('to') or None
        if f_date is not None and t_date is not None:
            from_date = convert_to_date(f_date)
            to_date = convert_to_date(t_date)
            if from_date > to_date:
                from_date, to_date = to_date, from_date
            if (to_date - from_date).days > 365:
                to_date = from_date + timedelta(days=365)
        else:
            from_date = datetime.now()
            to_date = from_date + timedelta(days=14)
            f_date = datetime.strftime(from_date, "%d.%m.%Y")
            t_date = datetime.strftime(to_date, "%d.%m.%Y")
        if from_date < to_date:
            self.search_dates = {'from_date': f_date, 'to_date': t_date}
        else:
            from_date, to_date = to_date, from_date
            self.search_dates = {'from_date': t_date, 'to_date': f_date}
        return Bill.objects.for_object(self.object)


class RequestAddHotelView(CreateView):
    model = RequestAddHotel
    form_class = RequestAddHotelForm
    template_name = "requests/add.html"

    def get_form_kwargs(self):
        kwargs = super(RequestAddHotelView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_success_url(self):
        return reverse('hotel_list')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(RequestAddHotelView, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.count()
        context['title_line'] = _('request for add hotel')
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if self.request.user.is_authenticated():
            self.object.user = self.request.user
        self.object.ip = self.request.META['REMOTE_ADDR']
        self.object.user_agent = self.request.META['HTTP_USER_AGENT']
        self.object.save()
        request_add_hotel_mail(self.object)
        return super(RequestAddHotelView, self).form_valid(form)


class BookingsList(CurrentUserSuperuser, ListView):
    model = Booking
    paginate_by = 20
    template_name = "sysadm/bookings.html"
    search_dates = dict()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BookingsList, self).get_context_data(**kwargs)
        context['tab'] = 'bookings'
        context['title_line'] = _('booking list')
        context['search_dates'] = self.search_dates
        return context

    def get_queryset(self):
        try:
            f_date = self.request.GET.get('from')
            from_date = convert_to_date(f_date)
            t_date = self.request.GET.get('to')
            to_date = convert_to_date(t_date)
            if from_date > to_date:
                from_date, to_date = to_date, from_date
                self.search_dates = {'from_date': t_date, 'to_date': f_date}
            else:
                self.search_dates = {'from_date': f_date, 'to_date': t_date}
            return Booking.objects.select_related().filter(date__range=(from_date, to_date))
        except:
            return Booking.objects.select_related().all()


class RequestsList(CurrentUserSuperuser, ListView):
    paginate_by = 10
    model = RequestAddHotel
    template_name = "sysadm/requests.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(RequestsList, self).get_context_data(**kwargs)
        context['tab'] = 'requests'
        context['title_line'] = _('request for add')
        return context


class ReportsList(CurrentUserSuperuser, TemplateView):
    template_name = "sysadm/reports.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ReportsList, self).get_context_data(**kwargs)
        context['tab'] = 'reports'
        context['title_line'] = _('site reports')
        return context


class ReportView(CurrentUserSuperuser, ListView):
    paginate_by = 50
    model = Hotel
    template_name = "sysadm/report.html"

    def get_queryset(self):
        report_type = self.kwargs['slug'] or None
        self.report_name = _('Error')
        result = None
        if report_type == 'all':
            result = Hotel.objects.select_related().all()
            self.report_name = _('All hotels in system')
        elif report_type == 'notsetpayment':
            result = Hotel.objects.select_related().filter(payment_method=None)
            self.report_name = _('Hotels without payment methods')
        elif report_type == 'setpayment':
            result = Hotel.objects.select_related().exclude(payment_method=None)
            self.report_name = _('Hotels with payment methods')
        elif report_type == 'notsetadmins':
            result = Hotel.objects.select_related().filter(admins=None)
            self.report_name = _('Hotels without admins')
        elif report_type == 'setadmins':
            result = Hotel.objects.select_related().exclude(admins=None)
            self.report_name = _('Hotels with admins')
        elif report_type == 'onrequest':
            result = Hotel.objects.select_related().filter(work_on_request=True)
            self.report_name = _('Hotels, works on request')
        elif report_type == 'nullpercent':
            result = Hotel.objects.select_related().filter(agentpercent__date__lte=datetime.now()).\
                annotate(Max('agentpercent__date')).filter(agentpercent__percent=0,
                                                           agentpercent__date__max=F('agentpercent__date'))
            self.report_name = _('Hotels, with current null percent')
        elif report_type == 'city':
            result = City.objects.order_by('name')
            self.report_name = _('Total cities')
            self.template_name = "sysadm/report_city.html"
        if report_type != 'city' and result:
            result = result.order_by('city__name', 'name')
        self.report_arg = report_type
        return result

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ReportView, self).get_context_data(**kwargs)
        context['tab'] = 'reports'
        context['title_line'] = _('site reports')
        context['report_name'] = self.report_name
        context['report_arg'] = self.report_arg
        return context


class UserCabinet(CurrentUserCabinetAccess, UpdateView):
    form_class = UserCabinetInfoForm
    template_name = "usercabinet/info.html"

    def get_form_kwargs(self):
        kwargs = super(UserCabinet, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_object(self, queryset=None):
        user = get_object_or_404(get_user_model(), username=self.kwargs['username'])
        return user

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(UserCabinet, self).get_context_data(**kwargs)
        context['tab'] = 'info'
        context['title_line'] = _('private cabinet')
        return context

    def get_success_url(self):
        return reverse('user_profile', args=[self.object.username])


class UserBookings(CurrentUserCabinetAccess, SingleObjectMixin, ListView):
    paginate_by = 5
    template_name = "usercabinet/bookings.html"

    def get_object(self, queryset=None):
        user = get_object_or_404(get_user_model(), username=self.kwargs['username'])
        return user

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        kwargs['object'] = self.object
        context = super(UserBookings, self).get_context_data(**kwargs)
        context['tab'] = 'bookings'
        context['title_line'] = _('bookings')
        return context

    def get_queryset(self):
        self.object = self.get_object()
        try:
            f_date = self.request.GET.get('from')
            from_date = convert_to_date(f_date)
            t_date = self.request.GET.get('to')
            to_date = convert_to_date(t_date)
            if from_date > to_date:
                from_date, to_date = to_date, from_date
            return Booking.objects.select_related().filter(user=self.object, date__range=(from_date, to_date))
        except:
            return Booking.objects.select_related().filter(user=self.object)


class UserBookingDetail(CurrentUserBookingAccess, DetailView):
    model = Booking
    slug_field = 'uuid'
    template_name = "usercabinet/booking.html"

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(UserBookingDetail, self).get_context_data(**kwargs)
        context['title_line'] = _('Booking ID') + ' ' + self.object.uuid
        context['tab'] = 'bookings'
        return context


class ClientBooking(RedirectHttpsView, DetailView):
    model = Hotel
    template_name = "booking/add.html"

    def get_object(self, queryset=None):
        room = get_object_or_404(Room.objects.select_related(), pk=self.kwargs['room'])
        return room.hotel

    def get_context_data(self, **kwargs):
        f_date = self.request.GET.get('from') or None
        t_date = self.request.GET.get('to') or None
        guests = guests_from_request(self.request)
        # TODO WTF
        if f_date == t_date:
            raise Http404
        if f_date and t_date and guests and ('room' in self.kwargs.keys()):
            try:
                room_id = int(self.kwargs['room'])
            except ValueError:
                raise Http404
            room = get_object_or_404(Room, id=room_id)
            if room.hotel.payment_method.count() < 1:
                raise Http404
            s = SettlementVariant.objects.filter(room=room).values_list('settlement', flat=True)
            if guests > max(s):
                raise Http404
            from_date = convert_to_date(f_date)
            to_date = convert_to_date(t_date)
            if from_date > to_date:
                f_date, t_date = t_date, f_date
                from_date, to_date = to_date, from_date
            if (from_date - datetime.now()).days < -1:
                raise Http404
            avail_count = Availability.objects.filter(room=room, date__range=(from_date, to_date - timedelta(days=1)),
                                                      placecount__gt=0).count()
            if avail_count != (to_date - from_date).days:
                raise Http404
            settlement = SettlementVariant.objects.filter(room=room, settlement__gte=guests,
                                                          enabled=True).order_by('settlement')[0]
            #settlement = get_object_or_404(SettlementVariant,room=room,settlement=guests,enabled=True)
            valid_price_count = PlacePrice.objects.filter(settlement=settlement,
                                                          date__range=(from_date, to_date - timedelta(days=1)),
                                                          amount__gt=0).count()
            if valid_price_count != (to_date - from_date).days:
                raise Http404
            context = super(ClientBooking, self).get_context_data(**kwargs)
            context['hotel_count'] = Hotel.objects.filter(city=self.object.city).count()
            context['tab'] = 'rates'
            context['hotel'] = self.object
            context['title_line'] = _('booking')
            context['room_id'] = room_id
            context['room'] = room
            context['settlements'] = s
            context['search_data'] = {'from_date': f_date, 'to_date': t_date, 'guests': guests}
            return context
        else:
            raise Http404


class ClientAddBooking(AjaxFormMixin, CreateView):
    model = Booking
    form_class = BookingAddForm

    def form_valid(self, form):
        use_card = False
        p_m = self.request.REQUEST.get('payment_method') or None
        if p_m:
            payment_method = PaymentMethod.objects.get(pk=int(p_m))
            card_number = self.request.REQUEST.get('card_number') or None
            card_holder = self.request.REQUEST.get('card_holder') or None
            card_valid = self.request.REQUEST.get('card_valid') or None
            card_cvv2 = self.request.REQUEST.get('card_cvv2') or None
            if payment_method.use_card:
                if card_number and card_holder and card_valid and card_cvv2:
                    if not is_luhn_valid(card_number):
                        payload = {'success': False, 'engine_error': _('Card number is wrong.')}
                        return AjaxLazyAnswer(payload)
                    else:
                        use_card = True
                        try:
                            if len(card_cvv2) != 3:
                                raise ValueError
                            if len(card_valid) != 5:
                                raise ValueError
                            card_cvv2 = int(card_cvv2)
                        except ValueError:
                            payload = {'success': False, 'engine_error': _('Card CVV2 is wrong.')}
                            return AjaxLazyAnswer(payload)
                else:
                    payload = {'success': False, 'engine_error': _('You enter not all data of card.')}
                    return AjaxLazyAnswer(payload)
        else:
            payload = {'success': False, 'engine_error': _('You are not select payment method.')}
            return AjaxLazyAnswer(payload)
        self.object = form.save(commit=False)
        if self.request.user.is_authenticated():
            self.object.user = self.request.user
        room = Room.objects.get(id=form.cleaned_data.get('room_id'))
        settlement = SettlementVariant.objects.get(room=room, settlement=form.cleaned_data.get('settlement'))
        self.object.settlement = settlement
        self.object.hotel = settlement.room.hotel
        self.object.status = STATUS_ACCEPTED
        self.object.date = datetime.now()
        from_date = self.object.from_date
        to_date = self.object.to_date
        all_amount = Decimal(0)
        commission = Decimal(0)
        on_date = from_date
        while on_date < to_date:
            price = PlacePrice.objects.get(settlement=settlement, date=on_date)
            percent = self.object.hotel.get_percent_on_date(on_date)
            commission += (price.amount * percent) / 100
            all_amount += price.amount
            avail = Availability.objects.get(room=room, date=on_date)
            avail.placecount -= 1
            avail.save()
            on_date = on_date + timedelta(days=1)
        self.object.amount = all_amount
        self.object.hotel_sum = all_amount - commission
        self.object.commission = commission
        currency = Currency.objects.get(code=CURRENCY)
        self.object.currency = currency
        self.object.ip = self.request.META['REMOTE_ADDR']
        self.object.user_agent = self.request.META['HTTP_USER_AGENT']
        if use_card:
            self.object.card_number = card_number
            self.object.card_holder = card_holder
            self.object.card_valid = card_valid
            self.object.card_cvv2 = card_cvv2
        self.object.save()
        self.success_url = self.object.get_client_url()
        if self.request.user.is_authenticated:
            booking_new_client_mail(self.object, self.request.user.username)
        else:
            booking_new_client_mail(self.object)
        booking_new_hotel_mail(self.object)
        return super(ClientAddBooking, self).form_valid(form)


class RequestAdminAdd(CurrentUserSuperuser, TemplateView):
    template_name = 'sysadm/request.html'

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(RequestAdminAdd, self).get_context_data(**kwargs)
        context['tab'] = 'requests'
        context['title_line'] = _('request for add')
        context['request_hotel'] = RequestAddHotel.objects.get(id=self.kwargs['pk'])
        return context


class HotelMainPage(TemplateView):
    template_name = 'hotels/intro.html'

    def get_context_data(self, **kwargs):
        context = super(HotelMainPage, self).get_context_data(**kwargs)
        context['title_line'] = _('booking of russian hotels')
        return context


class BookingHotelDetail(CurrentUserHotelBookingAccess, DetailView):
    model = Booking
    slug_field = 'uuid'
    template_name = "cabinet/booking.html"

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(BookingHotelDetail, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.hotel.city).count()
        context['hotel'] = self.object.hotel
        context['title_line'] = _('Booking ID') + ' ' + self.object.uuid
        context['tab'] = 'reports'
        return context


class BookingAdminDetail(CurrentUserSuperuser, DetailView):
    model = Booking
    slug_field = 'uuid'
    template_name = "sysadm/booking.html"

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(BookingAdminDetail, self).get_context_data(**kwargs)
        context['title_line'] = _('Booking ID') + ' ' + self.object.uuid
        context['tab'] = 'bookings'
        return context


class BookingStatusChange(CurrentUserHotelBookingAccess, UpdateView):
    model = Booking
    slug_field = 'uuid'
    form_class = BookingStatusForm
    template_name = "cabinet/booking_status.html"

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(BookingStatusChange, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.hotel.city).count()
        context['hotel'] = self.object.hotel
        context['title_line'] = _('Booking ID') + ' ' + self.object.uuid
        context['tab'] = 'reports'
        return context

    def form_valid(self, form):
        booking = get_object_or_404(Booking, uuid=self.kwargs['slug'])
        self.object = form.save(commit=False)
        if self.object.status != booking.status:
            desc = self.request.POST.get('description') or None
            subject = _("Changed status of booking")
            message = _("Hotel: ") + self.object.hotel.get_name + "\n"
            message += _("Booking: ") + str(self.object.system_id) + "\n"
            message += _("Booking link: ") + self.object.get_absolute_url() + "\n"
            message += _("Old status: ") + booking.get_status_display() + "\n"
            message += _("New status: ") + self.object.get_status_display() + "\n"
            if desc is not None:
                message += _("Description: ") + desc + "\n"
            message += '\n' + "IP: %s USER-AGENT: %s" % (self.request.META.get('REMOTE_ADDR', ''),
                                                         self.request.META.get('HTTP_USER_AGENT', '')[:255]) + '\n'
            mail_managers(subject, message)
            self.object.save()
        return super(BookingStatusChange, self).form_valid(form)

    def get_success_url(self):
        return reverse('cabinet_bookings', args=[self.object.hotel.city.slug, self.object.hotel.slug])
