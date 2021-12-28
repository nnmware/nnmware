# nnmware(c)2012-2020

from __future__ import unicode_literals

from datetime import timedelta
from decimal import Decimal
from functools import reduce
from hashlib import sha1
from operator import and_

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Count, Sum, Max, F, Min, Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.list import ListView

from nnmware.apps.address.models import City
from nnmware.apps.booking.ajax import CardError
from nnmware.apps.booking.forms import CabinetInfoForm, CabinetRoomForm, \
    CabinetEditBillForm, RequestAddHotelForm, UserCabinetInfoForm, BookingAddForm
from nnmware.apps.booking.models import Hotel, Room, RoomOption, SettlementVariant, Availability, PlacePrice, \
    STATUS_ACCEPTED, HotelOption, Booking, RequestAddHotel, BOOKING_GB, BOOKING_NR, BOOKING_UB, \
    HotelSearch
from nnmware.apps.booking.templatetags.booking_tags import convert_to_client_currency, user_rate_from_request
from nnmware.apps.booking.utils import booking_new_client_mail
from nnmware.apps.booking.utils import guests_from_request, booking_new_sysadm_mail, request_add_hotel_mail
from nnmware.apps.money.models import Bill, Currency, BILL_UNKNOWN
from nnmware.core.ajax import ajax_answer_lazy
from nnmware.core.decorators import ssl_required
from nnmware.core.financial import is_luhn_valid
from nnmware.core.utils import convert_to_date, daterange, random_pw, send_template_mail, setting
from nnmware.core.views import AjaxViewMixin, UserToFormMixin
from nnmware.core.views import AttachedImagesMixin, AttachedFilesMixin, AjaxFormMixin, \
    CurrentUserSuperuser, RedirectHttpView, RedirectHttpsView


class CurrentUserHotelAdmin(View):
    """ Generic update view that check request.user is author of object """

    @method_decorator(ssl_required)
    @method_decorator(ensure_csrf_cookie)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user not in self.object.admins.all() and not request.user.is_superuser:
            raise Http404
        return super(CurrentUserHotelAdmin, self).dispatch(request, *args, **kwargs)


class CurrentUserRoomAdmin(View):
    """ Generic update view that check request.user is author of object """

    @method_decorator(ssl_required)
    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Room.objects.select_related(), pk=kwargs['pk'])
        if request.user not in obj.hotel.admins.all() and not request.user.is_superuser:
            raise Http404
        return super(CurrentUserRoomAdmin, self).dispatch(request, *args, **kwargs)


class CurrentUserHotelBillAccess(View):
    """ Generic update view that check request.user may view bills of hotel """

    @method_decorator(ssl_required)
    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Bill.objects.select_related(), pk=kwargs['pk'])
        if request.user not in obj.content_object.admins.all() and not request.user.is_superuser:
            raise Http404
        return super(CurrentUserHotelBillAccess, self).dispatch(request, *args, **kwargs)


class CurrentUserHotelBookingAccess(View):
    """ Generic update view that check request.user may view bookings of hotel """

    @method_decorator(ssl_required)
    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Booking.objects.select_related(), uuid=kwargs['slug'])
        if request.user not in obj.hotel.admins.all() and not request.user.is_superuser:
            raise Http404
        return super(CurrentUserHotelBookingAccess, self).dispatch(request, *args, **kwargs)


class CurrentUserBookingAccess(View):
    """ Generic update view that check request.user may view bookings of hotel """

    @method_decorator(ssl_required)
    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Booking.objects.select_related(), uuid=kwargs['slug'])
        # if obj.user:
        #     if (request.user != obj.user) and not request.user.is_superuser:
        #         raise Http404
        return super(CurrentUserBookingAccess, self).dispatch(request, *args, **kwargs)


class CurrentUserCabinetAccess(View):
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


def default_search():
    return {'from_date': (now() + timedelta(days=1)).strftime("%d.%m.%Y"),
            'to_date': (now() + timedelta(days=2)).strftime("%d.%m.%Y"), 'guests': 1, 'no_dates': 1}


class HotelList(AjaxViewMixin, RedirectHttpView, ListView):
    paginate_by = 20
    model = Hotel
    template_name = "hotels/list.html"
    search = 0

    def post(self, request, *args, **kwargs):
        return super(HotelList, self).get(request, *args, **kwargs)

    def get_queryset(self):
        key = sha1('%s' % (self.request.get_full_path(),)).hexdigest()
        searched_date = False
        self.search_data = dict()
        order = self.request.GET.get('order') or None
        sort = self.request.GET.get('sort') or None
        guests = guests_from_request(self.request)
        f_date = self.request.GET.get('from') or None
        t_date = self.request.GET.get('to') or None
        with_amount = self.request.POST.get('with_amount') or None
        amount_min = self.request.POST.get('amount_min') or None
        amount_max = self.request.POST.get('amount_max') or None
        options = self.request.POST.getlist('options') or None
        stars = self.request.POST.getlist('stars') or None
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
                    try:
                        h_s = HotelSearch()
                        h_s.date = now()
                        h_s.from_date = from_date
                        h_s.to_date = to_date
                        if guests:
                            h_s.guests = guests
                        if self.request.user.is_authenticated:
                            h_s.user = self.request.user
                        h_s.user_agent = self.request.META.get('HTTP_USER_AGENT', '')[:255]
                        h_s.ip = self.request.META.get('REMOTE_ADDR', '')
                        h_s.city = self.kwargs['slug']
                        h_s.save()
                    except:
                        pass
                    self.search_data['city'] = self.city
                    if stars:
                        self.search_data['stars'] = stars
                    if options:
                        self.search_data['options'] = options
                    if (from_date - now()).days < -1:
                        self.result_count = 0
                        return []
                    searched_date = True
                except:
                    pass
            self.search = 1
        self.result_count = None
        if self.request.is_ajax():
            self.template_name = "hotels/list_ajax.html"
            path = self.request.POST.get('path') or None
            if path:
                key = sha1('%s' % (path,)).hexdigest()
        data_key = cache.get(key)
        if not data_key:
            search_hotel = Hotel.objects.select_related('city').exclude(payment_method=None)
            if self.city:
                search_hotel = search_hotel.filter(Q(city=self.city) | Q(addon_city=self.city))
            if searched_date:
                # Find all rooms pk for this guest count
                need_days = (to_date - from_date).days
                date_period = (from_date, to_date - timedelta(days=1))
                rooms_list = SettlementVariant.objects.filter(enabled=True, settlement__gte=guests,
                    placeprice__date__range=date_period, placeprice__amount__gt=0).annotate(num_days=Count('pk')).\
                    filter(num_days__gte=need_days).order_by('room__pk').values_list('room__pk', flat=True).distinct()
                # searched_hotels_list = Room.objects.filter(pk__in=rooms_list, availability__date__range=date_period,
                #     availability__min_days__lte=need_days, availability__placecount__gt=0).\
                #     annotate(num_days=Count('pk')).filter(num_days__gte=need_days).order_by('hotel').\
                #     values_list('hotel__pk', flat=True).distinct()
                searched_hotels_list = Room.objects.filter(pk__in=rooms_list, availability__date__range=date_period,
                    availability__placecount__gt=0).\
                    annotate(num_days=Count('pk')).filter(num_days__gte=need_days).order_by('hotel').\
                    values_list('hotel__pk', flat=True).distinct()
                searched_hotels_not_avail = Room.objects.filter(pk__in=rooms_list,
                    availability__date__range=date_period, availability__min_days__gt=need_days).\
                    annotate(num_days=Count('pk')).filter(num_days__gt=0).order_by('hotel').\
                    values_list('hotel__pk', flat=True).distinct()
                search_hotel = search_hotel.filter(pk__in=list(searched_hotels_list), work_on_request=False).\
                    exclude(pk__in=list(searched_hotels_not_avail))
            hotels_pk_list = search_hotel.values_list('pk', flat=True).distinct()
            cache.set(key, hotels_pk_list, 300)
        else:
            search_hotel = Hotel.objects.select_related('city').filter(pk__in=data_key)
        if with_amount and amount_max and amount_min:
            self.search_data['amount'] = [amount_min, amount_max]
            if searched_date:
                hotels_with_amount = PlacePrice.objects.filter(date=from_date,
                    amount__range=(amount_min, amount_max)).values_list('settlement__room__hotel__pk',
                    flat=True).distinct()
            else:
                hotels_with_amount = PlacePrice.objects.filter(date=now(),
                    amount__range=(amount_min, amount_max)).values_list('settlement__room__hotel__pk',
                    flat=True).distinct()
            search_hotel = search_hotel.filter(pk__in=hotels_with_amount)
        if options:
            search_hotel = search_hotel.filter(reduce(and_, [Q(option=option) for option in options]))
        if stars:
            search_hotel = search_hotel.filter(starcount__in=stars)
        if order:
            self.tab, ui_order = hotel_order(self.tab, order, sort)
            search_hotel = search_hotel.order_by(ui_order)
        if not f_date and not t_date:
            self.search_data = default_search()
        result = search_hotel.annotate(Count('review'))
        self.result_count = result.count()
        if result:  # and self.request.is_ajax():
            amounts = PlacePrice.objects.filter(date__gte=now(), amount__gt=0,
                settlement__room__hotel__in=result).aggregate(Min('amount'), Max('amount'))
            if not amounts['amount__min']:
                amounts['amount__min'] = 0
            if not amounts['amount__max']:
                amounts['amount__max'] = 0
            rate = user_rate_from_request(self.request)
            self.payload['amount_min'] = convert_to_client_currency(int(amounts['amount__min']), rate)
            self.payload['amount_max'] = convert_to_client_currency(int(amounts['amount__max']), rate)
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
            context['city'] = self.city
        context['search_data'] = self.search_data
        context['hotels_in_city'] = self.result_count
        context['panel_for'] = 'hotels'
        context['amount_min'] = self.payload['amount_min']
        context['amount_max'] = self.payload['amount_max']
        return context


class HotelAdminList(ListView):
    model = Hotel
    paginate_by = 50
    template_name = "usercabinet/list.html"

    def get_queryset(self):
        if self.request.user.is_authenticated:
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
        if not hasattr(self, 'object'):
            self.object = get_object_or_404(Hotel.objects.select_related(), city__slug=self.kwargs['city'],
                                            slug=self.kwargs['slug'])
        return self.object

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
        options = self.request.POST.getlist('options') or None
        # Call the base implementation first to get a context
        context = super(HotelDetail, self).get_context_data(**kwargs)
        context['tab'] = 'rooms'
        context['city'] = self.object.city
        context['hotels_in_city'] = Hotel.objects.filter(city=self.object.city).count()
        context['title_line'] = self.object.get_name
        context['hotel_options'] = self.object.option.select_related().order_by('category', 'position', 'name')
        context['search_url'] = self.object.get_absolute_url()
        if self.request.is_ajax():
            self.template_name = "hotels/rooms_ajax.html"
        if f_date and t_date and guests:
            from_date = convert_to_date(f_date)
            to_date = convert_to_date(t_date)
            if from_date > to_date:
                from_date, to_date = to_date, from_date
                f_date, t_date = t_date, f_date
            try:
                h_s = HotelSearch()
                h_s.date = now()
                h_s.from_date = from_date
                h_s.to_date = to_date
                if guests:
                    h_s.guests = guests
                if self.request.user.is_authenticated:
                    h_s.user = self.request.user
                h_s.user_agent = self.request.META.get('HTTP_USER_AGENT', '')[:255]
                h_s.ip = self.request.META.get('REMOTE_ADDR', '')
                h_s.city = self.kwargs['city']
                h_s.hotel = self.kwargs['slug']
                h_s.save()
            except:
                pass
            need_days = (to_date - from_date).days
            if (from_date - now()).days < -1:
                rooms = []
            else:
                # Find all rooms pk for this guest count
                rooms = self.object.available_rooms_for_guests_in_period(guests, from_date, to_date)
            search_data = {'from_date': f_date, 'to_date': t_date, 'guests': guests, 'city': self.object.city}
            context['need_days'] = need_days
        else:
            search_data = default_search()
            rooms = self.object.room_set.all()
            context['full_info'] = 1
        if options:
            for option in options:
                rooms = rooms.filter(option=option)
        context['rooms'] = rooms
        if rooms:
            self.payload['result_count'] = rooms.objects.count()
        else:
            self.payload['result_count'] = 0
        context['search'] = 1
        context['search_data'] = search_data
        context['panel_for'] = 'hotel'
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
        context['search_data'] = default_search()
        context['search'] = 1
        context['panel_for'] = 'hotel'
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
        context['search_data'] = default_search()
        context['search'] = 1
        context['panel_for'] = 'hotel'
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
        room_search = None
        if self.object.hotel is not None:
            context['city'] = self.object.hotel.city
            context['title_line'] = self.object.hotel.get_name
            context['hotels_in_city'] = Hotel.objects.filter(city=self.object.hotel.city).count()
            context['search_url'] = self.object.hotel.get_absolute_url()
            context['hotel'] = self.object.hotel
        context['tab'] = 'description'
        context['room_options'] = self.object.option.select_related().order_by('category', 'position', 'name')
        if f_date and t_date and guests:
            from_date = convert_to_date(f_date)
            to_date = convert_to_date(t_date)
            if from_date > to_date:
                from_date, to_date = to_date, from_date
                f_date, t_date = t_date, f_date
            try:
                h_s = HotelSearch()
                h_s.date = now()
                h_s.from_date = from_date
                h_s.to_date = to_date
                if guests:
                    h_s.guests = guests
                if self.request.user.is_authenticated:
                    h_s.user = self.request.user
                h_s.user_agent = self.request.META.get('HTTP_USER_AGENT', '')[:255]
                h_s.ip = self.request.META.get('REMOTE_ADDR', '')
                h_s.city = self.kwargs['city']
                h_s.hotel = self.kwargs['slug']
                h_s.save()
            except:
                pass
            need_days = (to_date - from_date).days
            if (from_date - now()).days < -1:
                search_data = default_search()
            else:
                date_period = (from_date, to_date - timedelta(days=1))
                available_days = Availability.objects.filter(room=self.object, date__range=date_period,
                                                        min_days__lte=need_days).count()
                if available_days >= need_days:
                    if SettlementVariant.objects.filter(enabled=True, settlement__gte=guests, room=self.object,
                        placeprice__date__range=date_period, placeprice__amount__gt=0).annotate(num_days=Count('pk')).\
                            filter(num_days__gte=need_days).exists():
                        searched_room_list = Availability.objects.filter(room=self.object, date__range=date_period,
                            placecount__gt=0).annotate(num_days=Sum('room')).filter(num_days__gte=need_days).\
                            order_by('room').values_list('room__pk', flat=True).distinct()
                        room_with_amount_list = PlacePrice.objects.filter(settlement__room=self.object,
                            date__range=date_period, amount__gte=0).annotate(num_days=Sum('settlement__room')).\
                            filter(num_days__gte=need_days).order_by('settlement__room').\
                            values_list('settlement__room__pk', flat=True).distinct()
                        rooms = Room.objects.select_related().filter(pk__in=searched_room_list).\
                            filter(pk__in=room_with_amount_list)
                        if rooms.exists():
                            room_search = 1
                search_data = {'from_date': f_date, 'to_date': t_date, 'guests': guests, 'city': self.object.hotel.city}
            context['room_found'] = room_search
            context['need_days'] = need_days
        else:
            search_data = default_search()
            context['full_info'] = 1
        context['search_data'] = search_data
        context['search'] = 1
        context['panel_for'] = 'room'
        return context


class CabinetInfo(UserToFormMixin, HotelPathMixin, UpdateView, CurrentUserHotelAdmin):
    model = Hotel
    form_class = CabinetInfoForm
    template_name = "cabinet/info.html"

    def get_context_data(self, **kwargs):
        context = super(CabinetInfo, self).get_context_data(**kwargs)
        context['options_list'] = HotelOption.objects.select_related().order_by('category', 'position', 'name')
        context['tab'] = 'common'
        context['title_line'] = _('private cabinet')
        return context

    def get_success_url(self):
        return reverse('cabinet_info', args=[self.object.city.slug, self.object.slug])


class CabinetRooms(HotelPathMixin, CreateView, CurrentUserHotelAdmin):
    model = Room
    form_class = CabinetRoomForm
    template_name = "cabinet/rooms.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.hotel = self.hotel
        self.object.save()
        return super(CabinetRooms, self).form_valid(form)

    def get_context_data(self, **kwargs):
        self.hotel = get_object_or_404(Hotel.objects.select_related(), city__slug=self.kwargs['city'],
                                  slug=self.kwargs['slug'])
        context = super(CabinetRooms, self).get_context_data(**kwargs)
        context['options_list'] = RoomOption.objects.select_related('category').order_by('category', 'position', 'name')
        context['tab'] = 'rooms'
        context['hotel'] = self.hotel
        context['title_line'] = _('private cabinet')
        return context

    def get_success_url(self):
        return reverse('cabinet_room', args=[self.object.hotel.city.slug, self.object.hotel.slug, self.object.pk])


class CabinetEditRoom(UpdateView, CurrentUserRoomAdmin):
    model = Room
    pk_url_kwarg = 'pk'
    form_class = CabinetRoomForm
    template_name = "cabinet/room.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CabinetEditRoom, self).get_context_data(**kwargs)
        context['options_list'] = RoomOption.objects.select_related('category').order_by('category', 'position', 'name')
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
            # noinspection PyBroadException
            try:
                settlement = SettlementVariant.objects.get(room=self.object, settlement=variant)
                settlement.enabled = True
                settlement.save()
            except:
                SettlementVariant(room=self.object, settlement=variant, enabled=True).save()
        return super(CabinetEditRoom, self).form_valid(form)


class CabinetRates(HotelPathMixin, DetailView, CurrentUserHotelAdmin):
    model = Hotel
    template_name = "cabinet/rates.html"

    def post(self, request, *args, **kwargs):
        return super(CabinetRates, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        rooms = self.request.POST.getlist('room_id') or None
        f_date = self.request.POST.get('from') or None
        t_date = self.request.POST.get('to') or None
        days_of_week = self.request.POST.getlist('days_of_week') or None
        context = super(CabinetRates, self).get_context_data(**kwargs)
        context['tab'] = 'rates'
        context['hotel'] = self.object
        context['title_line'] = _('private cabinet')
        if rooms:
            context['rooms'] = Room.objects.filter(hotel=self.object, pk__in=rooms)
            context['rooms_lst'] = rooms
        else:
            try:
                context['rooms'] = [Room.objects.filter(hotel=self.object)[0]]
            except IndexError as ierr:
                context['rooms'] = None
        if f_date and t_date:
            context['from'] = f_date
            context['to'] = t_date
            from_date = convert_to_date(f_date)
            to_date = convert_to_date(t_date)
            if from_date > to_date:
                from_date, to_date = to_date, from_date
            if (to_date - from_date).days > 365:
                to_date = from_date + timedelta(days=365)
            date_gen = daterange(from_date, to_date + timedelta(days=1))
        else:
            from_date = now()
            to_date = from_date + timedelta(days=13)
            date_gen = daterange(from_date, to_date + timedelta(days=1))
            f_date = from_date.strftime('%d.%m.%Y')
            t_date = to_date.strftime('%d.%m.%Y')
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
        context['sheet_lst'] = self.request.POST.getlist('sheet') or True
        return context


class CabinetDiscount(HotelPathMixin, DetailView, CurrentUserHotelAdmin):
    model = Hotel
    template_name = "cabinet/discounts.html"
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(CabinetDiscount, self).get_context_data(**kwargs)
        context['rooms'] = Room.objects.filter(hotel=self.object)
        context['tab'] = 'discounts'
        context['title_line'] = _('discounts for hotel %s' % self.object.get_name)
        return context


class CabinetBillEdit(AttachedFilesMixin, UpdateView, CurrentUserSuperuser):
    model = Bill
    form_class = CabinetEditBillForm
    template_name = "cabinet/bill_edit.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CabinetBillEdit, self).get_context_data(**kwargs)
        context['tab'] = 'reports'
        context['hotel'] = self.object.content_object
        context['title_line'] = _('private cabinet')
        return context

    def get_success_url(self):
        return reverse('cabinet_bills', args=[self.object.content_object.city.slug, self.object.content_object.slug])


class CabinetBookings(HotelPathMixin, SingleObjectMixin, ListView, CurrentUserHotelAdmin):
    paginate_by = 20
    template_name = "cabinet/bookings.html"
    search_dates = dict()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        kwargs['object'] = self.object
        context = super(CabinetBookings, self).get_context_data(**kwargs)
        context['tab'] = 'reports'
        context['tab_small'] = 'bookings'
        context['hotel'] = self.object
        context['title_line'] = _('bookings')
        context['search_dates'] = self.search_dates
        return context

    def get_queryset(self):
        self.object = self.get_object()
        f_date = self.request.GET.get('from') or None
        t_date = self.request.GET.get('to') or None
        bookings = Booking.objects.filter(hotel=self.object)
        if f_date and t_date:
            from_date = convert_to_date(f_date)
            to_date = convert_to_date(t_date)
            if from_date > to_date:
                from_date, to_date = to_date, from_date
                f_date, t_date = t_date, f_date
            if (to_date - from_date).days > 365:
                to_date = from_date + timedelta(days=365)
                t_date = to_date.strftime('%d.%m.%Y')
            self.search_dates = {'from_date': f_date, 'to_date': t_date}
            bookings = bookings.filter(date__range=(from_date, to_date))
        return bookings.filter(enabled=True)


class CabinetBills(HotelPathMixin, SingleObjectMixin, ListView, CurrentUserHotelAdmin):
    template_name = "cabinet/bills.html"
    search_dates = dict()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        kwargs['object'] = self.object
        context = super(CabinetBills, self).get_context_data(**kwargs)
        context['tab'] = 'reports'
        context['tab_small'] = 'bills'
        context['hotel'] = self.object
        context['title_line'] = _('bills')
        context['search_dates'] = self.search_dates
        return context

    def get_queryset(self):
        self.object = self.get_object()
        f_date = self.request.GET.get('from') or None
        t_date = self.request.GET.get('to') or None
        bills = Bill.objects.for_object(self.object)
        if f_date and t_date:
            from_date = convert_to_date(f_date)
            to_date = convert_to_date(t_date)
            if from_date > to_date:
                from_date, to_date = to_date, from_date
                f_date, t_date = t_date, f_date
            if (to_date - from_date).days > 365:
                to_date = from_date + timedelta(days=365)
                t_date = to_date.strftime('%d.%m.%Y')
            self.search_dates = {'from_date': f_date, 'to_date': t_date}
            bills = bills.filter(date__range=(from_date, to_date))
        if not self.request.user.is_superuser:
            bills = bills.exclude(status=BILL_UNKNOWN)
        return bills.order_by('-date')


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
        if self.request.user.is_authenticated:
            self.object.user = self.request.user
        self.object.ip = self.request.META['REMOTE_ADDR']
        self.object.user_agent = self.request.META['HTTP_USER_AGENT']
        self.object.save()
        request_add_hotel_mail(self.object)
        return super(RequestAddHotelView, self).form_valid(form)


class BookingsList(ListView, CurrentUserSuperuser):
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
        result = Booking.objects.select_related('hotel', 'settlement', 'payment_method', 'hotel__city',
                                                'settlement__room', 'user').all()
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
            return result.filter(date__range=(from_date, to_date))
        except:
            return result


class RequestsList(ListView, CurrentUserSuperuser):
    paginate_by = 10
    model = RequestAddHotel
    template_name = "sysadm/requests.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(RequestsList, self).get_context_data(**kwargs)
        context['tab'] = 'requests'
        context['title_line'] = _('request for add')
        return context


class ReportsList(TemplateView, CurrentUserSuperuser):
    template_name = "sysadm/reports.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ReportsList, self).get_context_data(**kwargs)
        context['tab'] = 'reports'
        context['title_line'] = _('site reports')
        return context


class ReportView(ListView, CurrentUserSuperuser):
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
        elif report_type == 'non-correct':
            not_filled_room = Room.objects.filter(availability__date__range=(now(),
                now() + timedelta(days=13))).annotate(num_days=Count('pk')).filter(num_days__lt=14).\
                order_by('hotel').values_list('hotel__pk', flat=True).distinct()
            empty_avail_info = Room.objects.exclude(hotel__work_on_request=True).exclude(availability__date__range=
                (now(), now() + timedelta(days=13))).order_by('hotel').values_list('hotel__pk', flat=True).distinct()
            not_filled_amount = SettlementVariant.objects.exclude(placeprice__amount=0).\
                filter(enabled=True, placeprice__date__range=(now(),
                now() + timedelta(days=13))).annotate(num_days=Count('placeprice__pk')).\
                filter(num_days__lt=14).order_by('room__hotel').values_list('room__hotel__pk', flat=True).distinct()
            result = Hotel.objects.select_related().exclude(admins=None).exclude(work_on_request=True).\
                filter(Q(pk__in=not_filled_room) | Q(pk__in=not_filled_amount) | Q(pk__in=empty_avail_info))
            self.report_name = _('Hotels, not fully entered info')
        elif report_type == 'nullroom':
            nullroom = Room.objects.filter(availability__date__range=(now(),
                now() + timedelta(days=13)), availability__placecount=0).annotate(num_days=Count('pk')).\
                filter(num_days=14).order_by('hotel').values_list('hotel__pk', flat=True).distinct()
            result = Hotel.objects.select_related().exclude(admins=None).exclude(work_on_request=True).\
                filter(pk__in=nullroom)
            self.report_name = _('Hotels, which have null availability on 14 days')
        elif report_type == 'nullpercent':
            result = Hotel.objects.select_related().filter(agentpercent__date__lte=now()).\
                annotate(Max('agentpercent__date')).filter(agentpercent__percent=0,
                                                           agentpercent__date__max=F('agentpercent__date'))
            self.report_name = _('Hotels, with current null percent')
        elif report_type == 'city':
            result = City.objects.extra(select={'h_count': """SELECT COUNT(*) FROM booking_hotel WHERE
                (booking_hotel.enabled = 1 AND booking_hotel.city_id = address_city.id)"""}).order_by('name')
            self.report_name = _('Total cities')
            self.template_name = "sysadm/report_city.html"
        elif report_type == 'login':
            self.model = get_user_model()
            result = get_user_model().objects.annotate(Count('hotel')).filter(hotel__count__gt=0).\
                order_by('-last_login')
            self.report_name = _('Last hotel admin login')
            self.template_name = "sysadm/report_user.html"
        elif report_type == 'nologin':
            self.model = get_user_model()
            result = get_user_model().objects.annotate(Count('hotel')).filter(hotel__count__gt=0).\
                filter(last_login=F('date_joined')).order_by('-last_login')
            self.report_name = _('Admins hotel, who not entering')
            self.template_name = "sysadm/report_user.html"
        elif report_type == 'searched':
            self.model = HotelSearch
            result = HotelSearch.objects.select_related('user').order_by('-date')
            self.report_name = _('Searched parameters')
            self.template_name = "sysadm/report_searched.html"
        if report_type not in ['city', 'login', 'nologin', 'searched'] and result:
            result = result.order_by('city__name', 'name')
        self.report_arg = report_type
        if result:
            self.full_count = result.count()
        else:
            self.full_count = 0
        return result

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ReportView, self).get_context_data(**kwargs)
        context['tab'] = 'reports'
        context['title_line'] = _('site reports')
        context['full_count'] = self.full_count
        context['report_name'] = self.report_name
        context['report_name'] = self.report_name
        context['report_arg'] = self.report_arg
        return context


class UserCabinet(AjaxFormMixin, UpdateView, CurrentUserCabinetAccess):
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

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        password = self.request.POST["password"]
        if len(password.strip(' ')) > 0:
            if not self.request.user.check_password(password):
                self.request.user.set_password(password)
                self.request.user.save()
        return super(UserCabinet, self).form_valid(form)


class UserBookings(SingleObjectMixin, ListView, CurrentUserCabinetAccess):
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
        # noinspection PyBroadException
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


class BookingUserDetail(DetailView, CurrentUserBookingAccess):
    model = Booking
    slug_field = 'uuid'
    template_name = "usercabinet/booking.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BookingUserDetail, self).get_context_data(**kwargs)
        context['title_line'] = _('Booking ID') + ' ' + self.object.uuid
        context['tab'] = 'bookings'
        context['view_by'] = 'client'
        return context


class ClientBooking(DetailView, RedirectHttpsView):
    model = Hotel
    template_name = "booking/add.html"
    room = None

    def get_object(self, queryset=None):
        self.room = get_object_or_404(Room.objects.select_related(), pk=self.kwargs['room'])
        return self.room.hotel

    def get_context_data(self, **kwargs):
        f_date = self.request.GET.get('from') or None
        t_date = self.request.GET.get('to') or None
        btype = self.request.GET.get('btype') or None
        if btype not in ['ub', 'gb', 'nr']:
            raise Http404
        guests = guests_from_request(self.request)
        if f_date == t_date:
            raise Http404
        discount = self.room.simple_discount
        if f_date and t_date and guests:
            if btype == 'ub' and not discount.ub:
                raise Http404
            elif btype == 'gb' and not discount.gb:
                raise Http404
            elif btype == 'nr' and not discount.nr:
                raise Http404
            else:
                pass
            from_date = convert_to_date(f_date)
            to_date = convert_to_date(t_date)
            if from_date > to_date:
                f_date, t_date = t_date, f_date
                from_date, to_date = to_date, from_date
            if (from_date - now()).days < -1:
                raise Http404
            delta = (to_date - from_date).days
            date_period = (from_date, to_date - timedelta(days=1))
            avail_count = Availability.objects.filter(room=self.room, date__range=date_period, placecount__gt=0).count()
            if avail_count != (to_date - from_date).days:
                raise Http404
            try:
                settlement = SettlementVariant.objects.filter(room=self.room, settlement__gte=guests,
                    placeprice__date__range=date_period, placeprice__amount__gt=0).annotate(valid_s=Count('pk')).\
                    filter(valid_s__gte=delta).order_by('settlement').values_list('pk',
                    flat=True).distinct()[0]
            except:
                raise Http404
            context = super(ClientBooking, self).get_context_data(**kwargs)
            context['hotel_count'] = Hotel.objects.filter(city=self.object.city).count()
            context['tab'] = 'rates'
            context['title_line'] = _('booking')
            context['room_id'] = int(self.kwargs['room'])
            context['room'] = self.room
            context['settlement'] = settlement
            context['search_data'] = {'from_date': f_date, 'to_date': t_date, 'guests': guests}
            context['btype'] = btype
            return context
        else:
            raise Http404


class ClientAddBooking(UserToFormMixin, AjaxFormMixin, CreateView):
    model = Booking
    form_class = BookingAddForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        payload = None
        btype = self.request.POST.get('btype') or None
        guests = self.request.POST.get('guests') or None
        if guests is None or btype not in ['ub', 'gb', 'nr']:
            raise Http404
        if btype in ['gb', 'nr']:
            try:
                card_number = self.request.POST.get('card_number') or None
                card_holder = self.request.POST.get('card_holder') or None
                card_valid_month = self.request.POST.get('card_valid') or None
                card_valid_year = self.request.POST.get('card_valid_year') or None
                try:
                    if len(card_valid_month) == 2 and len(card_valid_year) == 2:
                        card_valid = '%s/%s' % (card_valid_month, card_valid_year)
                    else:
                        raise ValueError
                except:
                    payload = {'success': False, 'error': _('Card valid dates is wrong.')}
                    raise CardError
                card_cvv2 = self.request.POST.get('card_cvv2') or None
                if card_number and card_holder and card_valid and card_cvv2:
                    if not is_luhn_valid(card_number):
                        payload = {'success': False, 'error': _('Card number is wrong.')}
                        raise CardError
                    else:
                        try:
                            if len(card_cvv2) != 3 or len(card_valid) != 5:
                                raise ValueError
                            card_cvv2 = int(card_cvv2)
                        except:
                            payload = {'success': False, 'error': _('Card CVV2 is wrong.')}
                            raise CardError
                else:
                    payload = {'success': False, 'error': _('You enter not all data of card.')}
                    raise CardError
                self.object.card_number = card_number
                self.object.card_holder = card_holder
                self.object.card_valid = card_valid
                self.object.card_cvv2 = card_cvv2

            except CardError as carderr:
                return ajax_answer_lazy(payload)
        if self.request.user.is_authenticated:
            self.object.user = self.request.user
        else:
            email = form.cleaned_data.get('email')
            first_name = form.cleaned_data.get('first_name')[:30]
            last_name = form.cleaned_data.get('last_name')[:30]
            username = email[:30]
            password = random_pw()
            u = get_user_model()(username=username, email=email, first_name=first_name, last_name=last_name)
            u.set_password(password)
            u.is_active = True
            u.save()
            mail_dict = {'username': username, 'password': password,
                         'site_name': setting('SITENAME', 'www.nnmware.com')}
            subject = 'registration/new_user_subject.txt'
            body = 'registration/new_user.txt'
            send_template_mail(subject, body, mail_dict, [email])
            self.object.user = u
        room = Room.objects.get(id=form.cleaned_data.get('room_id'))
        settlement = SettlementVariant.objects.get(pk=form.cleaned_data.get('settlement'))
        self.object.settlement = settlement
        self.object.settlement_txt = str(settlement)
        self.object.hotel = settlement.room.hotel
        self.object.hotel_txt = str(settlement.room.hotel)
        self.object.status = STATUS_ACCEPTED
        self.object.date = now()
        if room.typefood:
            self.object.typefood = room.typefood
        room_discount = room.simple_discount
        discount = 0
        from_date = self.object.from_date
        to_date = self.object.to_date
        if btype == 'ub':
            booking_type = BOOKING_UB
            if 0 < room_discount.ub_discount < 100:
                discount = room_discount.ub_discount
        elif btype == 'gb':
            booking_type = BOOKING_GB
            if 0 < room_discount.gb_discount < 100:
                discount = room_discount.gb_discount
                if 0 < room_discount.gb_penalty < 101:
                    price_1day = PlacePrice.objects.get(settlement=settlement, date=from_date)
                    self.object.penaltycancel = (price_1day / 100) * room_discount.gb_penalty
                if room_discount.gb_days > 0:
                    self.object.freecancel = room_discount.gb_days
        elif btype == 'nr':
            booking_type = BOOKING_NR
            if 0 < room_discount.nr_discount < 100:
                discount = room_discount.nr_discount
        all_amount = Decimal(0)
        amount_no_discount = Decimal(0)
        commission = Decimal(0)
        on_date = from_date
        while on_date < to_date:
            price = PlacePrice.objects.get(settlement=settlement, date=on_date)
            percent = self.object.hotel.get_percent_on_date(on_date)
            day_price = price.amount
            amount_no_discount += day_price
            if discount > 0:
                day_price = (day_price * (100 - discount)) / 100
            commission += (day_price * percent) / 100
            all_amount += day_price
            avail = Availability.objects.get(room=room, date=on_date)
            avail.placecount -= 1
            avail.save()
            on_date = on_date + timedelta(days=1)
        self.object.amount = all_amount
        self.object.amount_no_discount = amount_no_discount
        self.object.hotel_sum = all_amount - commission
        self.object.commission = commission
        currency = Currency.objects.get(code=setting('CURRENCY', 'RUB'))
        self.object.currency = currency
        self.object.ip = self.request.META['REMOTE_ADDR']
        self.object.user_agent = self.request.META['HTTP_USER_AGENT']
        self.object.btype = booking_type
        if discount > 0:
            self.object.bdiscount = discount
        self.object.save()
        self.success_url = self.object.get_client_url()
        if not settings.DEBUG:
            if self.request.user.is_authenticated:
                booking_new_client_mail(self.object, self.request.user.username)
            else:
                booking_new_client_mail(self.object)
        booking_new_sysadm_mail(self.object)
        return super(ClientAddBooking, self).form_valid(form)


class RequestAdminAdd(TemplateView, CurrentUserSuperuser):
    template_name = 'sysadm/request.html'

    def get_context_data(self, **kwargs):
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
        context['from'] = now() + timedelta(days=1)
        context['to'] = now() + timedelta(days=2)
        return context


class BookingHotelDetail(DetailView, CurrentUserHotelBookingAccess):
    model = Booking
    slug_field = 'uuid'
    template_name = "cabinet/booking.html"

    def get_context_data(self, **kwargs):
        context = super(BookingHotelDetail, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.hotel.city).count()
        context['hotel'] = self.object.hotel
        context['title_line'] = _('Booking ID') + ' ' + self.object.uuid
        context['tab'] = 'reports'
        context['view_by'] = 'hotel'
        return context


class BookingAdminDetail(DetailView, CurrentUserSuperuser):
    model = Booking
    slug_field = 'uuid'
    template_name = "sysadm/booking.html"

    def get_context_data(self, **kwargs):
        context = super(BookingAdminDetail, self).get_context_data(**kwargs)
        context['title_line'] = _('Booking ID') + ' ' + self.object.uuid
        context['tab'] = 'bookings'
        context['view_by'] = 'admin'
        return context
