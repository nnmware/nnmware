# -*- coding: utf-8 -*-

from datetime import timedelta
from decimal import Decimal
from hashlib import sha1

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.mail import mail_managers
from django.db.models import Count, Sum, Max, F, Min, Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.list import ListView
from django.utils.translation import ugettext_lazy as _

from nnmware.apps.booking.forms import CabinetInfoForm, CabinetRoomForm, AddDiscountForm, \
    CabinetEditBillForm, RequestAddHotelForm, UserCabinetInfoForm, BookingAddForm, BookingStatusForm
from nnmware.apps.booking.models import Hotel, Room, RoomOption, SettlementVariant, Availability, PlacePrice, \
    STATUS_ACCEPTED, HotelOption, Discount, Booking, PaymentMethod, RequestAddHotel
from nnmware.apps.booking.utils import guests_from_request, booking_new_sysadm_mail, request_add_hotel_mail
from nnmware.core.ajax import ajax_answer_lazy
from nnmware.apps.booking.templatetags.booking_tags import convert_to_client_currency, user_rate_from_request
from nnmware.core.views import AttachedImagesMixin, AttachedFilesMixin, AjaxFormMixin, \
    CurrentUserSuperuser, RedirectHttpView, RedirectHttpsView
from nnmware.apps.money.models import Bill, Currency
from nnmware.core.utils import convert_to_date, daterange, random_pw, send_template_mail, setting
from nnmware.core.financial import is_luhn_valid
from nnmware.apps.booking.utils import booking_new_client_mail
from nnmware.apps.address.models import City
from nnmware.core.decorators import ssl_required
from nnmware.core.views import AjaxViewMixin, UserToFormMixin


class CurrentUserHotelAdmin(object):
    """ Generic update view that check request.user is author of object """

    @method_decorator(ssl_required)
    @method_decorator(ensure_csrf_cookie)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user in self.object.admins.all() and not request.user.is_superuser:
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
        # if obj.user:
        #     if (request.user != obj.user) and not request.user.is_superuser:
        #         raise Http404
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
            if self.city:
                search_hotel = Hotel.objects.select_related('city').filter(Q(city=self.city) | Q(addon_city=self.city)).\
                    exclude(payment_method=None)
            else:
                search_hotel = Hotel.objects.select_related('city').all().exclude(payment_method=None)
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
                search_hotel = search_hotel.filter(pk__in=searched_hotels_list, work_on_request=False).\
                    exclude(pk__in=searched_hotels_not_avail)
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
            for option in options:
                search_hotel = search_hotel.filter(option=option)
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
            need_days = (to_date - from_date).days
            if (from_date - now()).days < -1:
                rooms = []
            else:
                # Find all rooms pk for this guest count
                date_period = (from_date, to_date - timedelta(days=1))
                rooms_with_amount = SettlementVariant.objects.filter(enabled=True, settlement__gte=guests,
                    room__hotel=self.object, placeprice__date__range=date_period, placeprice__amount__gt=0).\
                    annotate(num_days=Count('pk')).\
                    filter(num_days__gte=need_days).order_by('room__pk').values_list('room__pk', flat=True).distinct()
                room_not_avail = Room.objects.filter(pk__in=rooms_with_amount,
                    availability__date__range=date_period, availability__min_days__gt=need_days).\
                    annotate(num_days=Count('pk')).filter(num_days__gt=0).order_by('pk').\
                    values_list('pk', flat=True).distinct()
                rooms = Room.objects.exclude(pk__in=room_not_avail).filter(pk__in=rooms_with_amount,
                    availability__date__range=date_period, availability__placecount__gt=0).\
                    annotate(num_days=Count('pk')).filter(num_days__gte=need_days)
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
            self.payload['result_count'] = rooms.count()
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


class CabinetInfo(UserToFormMixin, HotelPathMixin, CurrentUserHotelAdmin, AttachedImagesMixin, UpdateView):
    model = Hotel
    form_class = CabinetInfoForm
    template_name = "cabinet/info.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CabinetInfo, self).get_context_data(**kwargs)
        context['options_list'] = HotelOption.objects.select_related().order_by('category', 'position', 'name')
        context['tab'] = 'common'
        context['title_line'] = _('private cabinet')
        return context

    def get_success_url(self):
        return reverse('cabinet_info', args=[self.object.city.slug, self.object.slug])


class CabinetRooms(HotelPathMixin, CurrentUserHotelAdmin, CreateView):
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


class CabinetEditRoom(CurrentUserRoomAdmin, AttachedImagesMixin, UpdateView):
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
            except IndexError:
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


class CabinetDiscount(HotelPathMixin, CurrentUserHotelAdmin, DetailView):
    model = Hotel
    template_name = "cabinet/discounts.html"
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(CabinetDiscount, self).get_context_data(**kwargs)
        context['rooms'] = Room.objects.filter(hotel=self.object)
        context['tab'] = 'discounts'
        context['title_line'] = _('discounts for hotel %s' % self.object.get_name)
        return context


class CabinetBillEdit(CurrentUserHotelBillAccess, AttachedFilesMixin, UpdateView):
    model = Bill
    form_class = CabinetEditBillForm
    template_name = "cabinet/bill_edit.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CabinetBillEdit, self).get_context_data(**kwargs)
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
        context['tab'] = 'reports'
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


class CabinetBills(HotelPathMixin, CurrentUserHotelAdmin, SingleObjectMixin, ListView):
    template_name = "cabinet/bills.html"
    search_dates = dict()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        kwargs['object'] = self.object
        context = super(CabinetBills, self).get_context_data(**kwargs)
        context['tab'] = 'reports'
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
        return bills


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
        if report_type not in ['city', 'login', 'nologin'] and result:
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


class UserCabinet(AjaxFormMixin, CurrentUserCabinetAccess, UpdateView):
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
        btype = self.request.GET.get('btype') or None
        if btype not in ['ub', 'gb', 'nr']:
            raise Http404
        guests = guests_from_request(self.request)
        if f_date == t_date:
            raise Http404
        if f_date and t_date and guests and ('room' in self.kwargs.keys()):
            try:
                room_id = int(self.kwargs['room'])
            except ValueError:
                raise Http404
            room = get_object_or_404(Room, id=room_id)
            if btype == 'ub' and not room.simple_discount.ub:
                raise Http404
            elif btype == 'gb' and not room.simple_discount.gb:
                raise Http404
            elif btype == 'nr' and not room.simple_discount.nr:
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
            avail_count = Availability.objects.filter(room=room, date__range=date_period, placecount__gt=0).count()
            if avail_count != (to_date - from_date).days:
                raise Http404
            try:
                settlement = SettlementVariant.objects.filter(room=room, settlement__gte=guests,
                    placeprice__date__range=date_period, placeprice__amount__gt=0).annotate(valid_s=Count('pk')).\
                    filter(valid_s__gte=delta).order_by('settlement').values_list('pk',
                    flat=True).distinct()[0]
            except:
                raise Http404
            context = super(ClientBooking, self).get_context_data(**kwargs)
            context['hotel_count'] = Hotel.objects.filter(city=self.object.city).count()
            context['tab'] = 'rates'
            context['title_line'] = _('booking')
            context['room_id'] = room_id
            context['room'] = room
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
        use_card = False
        p_m = self.request.POST.get('payment_method') or None
        payload = None
        if p_m:
            payment_method = PaymentMethod.objects.get(pk=int(p_m))
            card_number = self.request.POST.get('card_number') or None
            card_holder = self.request.POST.get('card_holder') or None
            card_valid = self.request.POST.get('card_valid') or None
            card_cvv2 = self.request.POST.get('card_cvv2') or None
            if payment_method.use_card:
                if card_number and card_holder and card_valid and card_cvv2:
                    if not is_luhn_valid(card_number):
                        payload = {'success': False, 'error': _('Card number is wrong.')}
                    else:
                        use_card = True
                        try:
                            if len(card_cvv2) != 3:
                                raise ValueError
                            if len(card_valid) != 5:
                                raise ValueError
                            card_cvv2 = int(card_cvv2)
                        except ValueError:
                            payload = {'success': False, 'error': _('Card CVV2 is wrong.')}
                else:
                    payload = {'success': False, 'error': _('You enter not all data of card.')}
        else:
            payload = {'success': False, 'error': _('You are not select payment method.')}
        if payload:
            return ajax_answer_lazy(payload)
        self.object = form.save(commit=False)
        if self.request.user.is_authenticated():
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
        currency = Currency.objects.get(code=setting('CURRENCY', 'RUB'))
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
        booking_new_sysadm_mail(self.object)
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
        context['from'] = now() + timedelta(days=1)
        context['to'] = now() + timedelta(days=2)
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
