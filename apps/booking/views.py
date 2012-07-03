# -*- coding: utf-8 -*-

from datetime import date, timedelta, datetime
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import Http404, get_host, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.base import View, TemplateView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import FormView, UpdateView, CreateView
from django.views.generic.list import ListView
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.booking.models import *
from nnmware.apps.booking.forms import *
from nnmware.apps.booking.utils import guests_from_request, booking_new_hotel_mail, request_add_hotel_mail
from nnmware.apps.userprofile.models import Profile
from nnmware.core.ajax import AjaxLazyAnswer
from nnmware.core.config import CURRENCY
from nnmware.core.views import AttachedImagesMixin, AttachedFilesMixin, AjaxFormMixin, CurrentUserSuperuser
from nnmware.apps.money.models import Bill, Currency
import time
from nnmware.core.utils import date_range, convert_to_date, daterange
from nnmware.core.financial import convert_from_client_currency
from nnmware.core.financial import is_luhn_valid
from nnmware.apps.booking.utils import booking_new_client_mail
from nnmware.core.decorators import ssl_required
from nnmware.apps.address.models import City

class CurrentUserHotelAdmin(object):
    """ Generic update view that check request.user is author of object """
    @method_decorator(ssl_required)
    def dispatch(self, request, *args, **kwargs):
        city = get_object_or_404(City, slug=kwargs['city'])
        obj = get_object_or_404(Hotel,city=city,slug=kwargs['slug'])
        if not request.user in obj.admins.all() and not request.user.is_superuser:
            raise Http404
        return super(CurrentUserHotelAdmin, self).dispatch(request, *args, **kwargs)

class CurrentUserRoomAdmin(object):
    """ Generic update view that check request.user is author of object """

    @method_decorator(ssl_required)
    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Room, pk=kwargs['pk'])
        if not request.user in obj.hotel.admins.all() and not request.user.is_superuser:
            raise Http404
        return super(CurrentUserRoomAdmin, self).dispatch(request, *args, **kwargs)


class CurrentUserHotelBillAccess(object):
    """ Generic update view that check request.user may view bills of hotel """

    @method_decorator(ssl_required)
    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Bill, pk=kwargs['pk'])
        if not request.user in obj.target.admins.all() and not request.user.is_superuser:
            raise Http404
        return super(CurrentUserHotelBillAccess, self).dispatch(request, *args, **kwargs)

class CurrentUserHotelBookingAccess(object):
    """ Generic update view that check request.user may view bookings of hotel """

    @method_decorator(ssl_required)
    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Booking, uuid=kwargs['slug'])
        if not request.user in obj.hotel.admins.all() and not request.user.is_superuser:
            raise Http404
        return super(CurrentUserHotelBookingAccess, self).dispatch(request, *args, **kwargs)

class CurrentUserBookingAccess(object):
    """ Generic update view that check request.user may view bookings of hotel """

    @method_decorator(ssl_required)
    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Booking, uuid=kwargs['slug'])
        if obj.user:
            if (request.user <> obj.user) and not request.user.is_superuser:
                raise Http404
        return super(CurrentUserBookingAccess, self).dispatch(request, *args, **kwargs)

class CurrentUserCabinetAccess(object):

    @method_decorator(ssl_required)
    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(User, username=kwargs['username'])
        if not (request.user == obj) and not request.user.is_superuser:
            raise Http404
        return super(CurrentUserCabinetAccess, self).dispatch(request, *args, **kwargs)

class RedirectHttpsView(object):

    @method_decorator(ssl_required)
    def dispatch(self, request, *args, **kwargs):
        return super(RedirectHttpsView, self).dispatch(request, *args, **kwargs)

class HotelList(ListView):
    paginate_by = 20
    model = Hotel
    template_name = "hotels/list.html"

    def get_queryset(self):
        self.search_data = dict()
        order = self.request.GET.get('order') or None
        sort = self.request.GET.get('sort') or None
        options = self.request.GET.getlist('options') or None
        stars = self.request.GET.getlist('stars') or None
        notknowndates = self.request.GET.get('notknowndates') or None
        guests = guests_from_request(self.request)
        f_date = self.request.GET.get('from') or None
        t_date = self.request.GET.get('to') or None
        amount_min = self.request.GET.get('amount_min') or None
        amount_max = self.request.GET.get('amount_max') or None
        if amount_min:
            a_min = convert_from_client_currency(self.request, amount_min)
        if amount_max:
            a_max = convert_from_client_currency(self.request, amount_max)
        try:
            self.city = City.objects.get(slug=self.kwargs['slug'])
            hotels = Hotel.objects.filter(city=self.city)
        except :
            self.city = None
            hotels = Hotel.objects.all()
        self.tab = {'css_name':'asc','css_class':'desc','css_amount':'desc','css_review':'desc',
                    'order_name':'desc','order_class':'desc','order_amount':'desc','order_review':'desc',
                    'tab':'name'}

        if (notknowndates and self.city ) or (f_date and t_date and self.city):
            result = []
            try:
                from_date = convert_to_date(f_date)
                to_date = convert_to_date(t_date)
                if from_date > to_date:
                    self.search_data = {'from_date':t_date, 'to_date':f_date, 'guests':guests}
                    from_date, to_date = to_date, from_date
                else:
                    self.search_data = {'from_date':f_date, 'to_date':t_date, 'guests':guests}
                self.search_data['city'] = self.city
                for hotel in hotels:
                    if hotel.free_room(from_date,to_date,guests):
                        result.append(hotel.pk)
                search_hotel = Hotel.objects.filter(pk__in=result)
            except :
                search_hotel = hotels
            self.search = 1
        else :
            self.search = 0
            search_hotel = hotels
        if amount_max and amount_min:
            r = []
            for h in search_hotel:
                amount = h.min_current_amount
                if int(a_min) < amount < int(a_max):
                    r.append(h.pk)
            search_hotel = Hotel.objects.filter(pk__in=r)
        if options:
            for option in options:
                search_hotel = search_hotel.filter(option=option)
        if stars:
            search_hotel = search_hotel.filter(starcount__in=stars)
        if order:
            if order == 'name':
                self.tab['tab'] = 'name'
                if sort == 'desc':
                    result = search_hotel.order_by('-name')
                    self.tab['css_name'] = 'desc'
                    self.tab['order_name'] = 'asc'
                else:
                    result = search_hotel.order_by('name')
                    self.tab['css_name'] = 'asc'
                    self.tab['order_name'] = 'desc'
            elif order == 'class':
                self.tab['tab'] = 'class'
                if sort == 'asc':
                    result = search_hotel.order_by('starcount')
                    self.tab['css_class'] = 'asc'
                    self.tab['order_class'] = 'desc'
                else:
                    result = search_hotel.order_by('-starcount')
                    self.tab['css_class'] = 'desc'
                    self.tab['order_class'] = 'asc'
            elif order == 'amount':
                self.tab['tab'] = 'amount'
                if sort == 'asc':
                    result = search_hotel.order_by('current_amount')
                    self.tab['css_amount'] = 'asc'
                    self.tab['order_amount'] = 'desc'
                else:
                    result = search_hotel.order_by('-current_amount')
                    self.tab['css_amount'] = 'desc'
                    self.tab['order_amount'] = 'asc'
            elif order == 'review':
                self.tab['tab'] = 'review'
                if sort == 'asc':
                    result = search_hotel.order_by('point')
                    self.tab['css_review'] = 'asc'
                    self.tab['order_review'] = 'desc'
                else:
                    result = search_hotel.order_by('-point')
                    self.tab['css_review'] = 'desc'
                    self.tab['order_review'] = 'asc'
            else:
                pass
        else:
            result = search_hotel
        try:
            self.result_count = search_hotel.count()
        except:
            self.result_count = None
        return result

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(HotelList, self).get_context_data(**kwargs)
        context['title_line'] = _('list of hotels')
        context['tab'] = self.tab
        if self.search:
            context['search'] = self.search
            context['search_count'] = self.result_count
            context['search_data'] = self.search_data
        else:
            context['country'] = 1
        if self.city:
            context['city'] = self.city
            context['hotels_in_city'] = Hotel.objects.filter(city=self.city).count()
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
                result = Hotel.objects.filter(admins = self.request.user)
            return result.order_by('city__name','name')
        raise Http404

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(HotelAdminList, self).get_context_data(**kwargs)
        context['title_line'] = _('list of hotels')
        context['tab'] = _('admin of hotels')
        return context

class HotelPathMixin(object):

    def get_object(self, queryset=None):
        city = get_object_or_404(City, slug=self.kwargs['city'])
        return get_object_or_404(Hotel,city=city,slug=self.kwargs['slug'])


class HotelDetail(HotelPathMixin, AttachedImagesMixin, DetailView):
    model = Hotel
    template_name = "hotels/detail.html"


    def get_context_data(self, **kwargs):
        f_date = self.request.GET.get('from') or None
        t_date = self.request.GET.get('to') or None
        guests = guests_from_request(self.request)
        # Call the base implementation first to get a context
        context = super(HotelDetail, self).get_context_data(**kwargs)
        context['tab'] = 'description'
        context['city'] = self.object.city
        context['hotels_in_city'] = Hotel.objects.filter(city=self.object.city).count()
        context['title_line'] = self.object.get_name
        context['hotel_options'] = self.object.option.order_by('category','order_in_list','name')
        context['search_url'] = self.object.get_absolute_url()
        try:
            from_date = convert_to_date(f_date)
            to_date = convert_to_date(t_date)
            if from_date > to_date:
                from_date, to_date = to_date, from_date
                f_date, t_date = t_date, f_date
            context['free_room'] = self.object.free_room(from_date,to_date,guests)
            search_data = {'from_date':f_date, 'to_date':t_date, 'guests':guests, 'city':self.object.city}
            context['search'] = 1
            context['search_data'] = search_data
            context['search_count'] = Hotel.objects.filter(city=self.object.city).count()
        except :
            pass
        return context

class HotelLocation(HotelPathMixin, DetailView):
#    model = Hotel
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
        context['city'] = self.object.hotel.city
        context['hotels_in_city'] = Hotel.objects.filter(city=self.object.hotel.city).count()
        context['tab'] = 'description'
        context['title_line'] = self.object.hotel.get_name
        context['room_options'] = self.object.option.order_by('category','order_in_list','name')
        context['search_url'] = self.object.hotel.get_absolute_url()
        if f_date and t_date and guests:
            from_date = convert_to_date(f_date)
            to_date = convert_to_date(t_date)
            if from_date > to_date:
                f_date, t_date = t_date, f_date
            search_data = {'from_date': f_date, 'to_date': t_date, 'guests': guests, 'city': self.object.hotel.city}
            context['search_data'] = search_data
            context['search'] = 1
            context['search_count'] = Hotel.objects.filter(city=self.object.hotel.city).count()
        return context

class CabinetInfo(HotelPathMixin, CurrentUserHotelAdmin, AttachedImagesMixin, UpdateView):
    model = Hotel
    form_class = CabinetInfoForm
    template_name = "cabinet/info.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CabinetInfo, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.city).count()
        context['options_list'] = HotelOption.objects.order_by('category','order_in_list','name')
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
    form_class = CabinetAddRoomForm
    template_name = "cabinet/rooms.html"

    def form_valid(self, form):
        city = get_object_or_404(City, slug=self.kwargs['city'])
        hotel = get_object_or_404(Hotel, city=city, slug=self.kwargs['slug'])
        self.object = form.save(commit=False)
        self.object.hotel = hotel
        self.object.save()
        variants = self.request.POST.getlist('settlement')
        for variant in variants:
            try:
                settlement = SettlementVariant.objects.get(room=self.object, settlement =variant)
                if not settlement.enabled:
                    settlement.enabled = True
                    settlement.save()
            except :
                SettlementVariant(room=self.object,settlement=variant,enabled=True).save()
        return super(CabinetRooms, self).form_valid(form)

    def get_context_data(self, **kwargs):
        city = get_object_or_404(City, slug=self.kwargs['city'])
        hotel = get_object_or_404(Hotel, city=city, slug=self.kwargs['slug'])
        # Call the base implementation first to get a context
        context = super(CabinetRooms, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=hotel.city).count()
        context['options_list'] = RoomOption.objects.order_by('category','order_in_list','name')
        context['tab'] = 'rooms'
        context['hotel'] = hotel
        context['title_line'] = _('private cabinet')
        return context

    def get_success_url(self):
            return reverse('cabinet_room', args=[self.object.hotel.city.slug,self.object.hotel.slug,
                                                 self.object.pk])

class CabinetEditRoom(CurrentUserRoomAdmin, AttachedImagesMixin, UpdateView):
    model = Room
    pk_url_kwarg = 'pk'
    form_class = CabinetEditRoomForm
    template_name = "cabinet/room.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CabinetEditRoom, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.hotel.city).count()
        context['options_list'] = RoomOption.objects.order_by('category','order_in_list','name')
        context['tab'] = 'rooms'
        context['hotel'] = self.object.hotel
        context['title_line'] = _('private cabinet')
        return context

    def get_success_url(self):
        return reverse('cabinet_rooms', args=[self.object.hotel.city.slug,self.object.hotel.slug])

    def form_valid(self, form):
        variants = self.request.POST.getlist('settlement')
        SettlementVariant.objects.filter(room=self.object).update(enabled=False)
        for variant in variants:
            try:
                settlement = SettlementVariant.objects.get(room=self.object, settlement=variant)
                settlement.enabled = True
                settlement.save()
            except :
                SettlementVariant(room=self.object,settlement=variant, enabled=True).save()
        return super(CabinetEditRoom, self).form_valid(form)


class CabinetRates(HotelPathMixin, CurrentUserHotelAdmin, DetailView):
    model = Hotel
    template_name = "cabinet/rates.html"

    def get_context_data(self, **kwargs):
        f_date = self.request.GET.get('from') or None
        t_date = self.request.GET.get('to') or None
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
            if (to_date-from_date).days > 365:
                to_date = from_date+timedelta(days=365)
            date_gen = daterange(from_date, to_date)
        else :
            from_date = datetime.now()
            date_gen = daterange(from_date, from_date+timedelta(days=14))
        date_period = []
        for i in date_gen:
            date_period.append(i)
        context['dates'] = date_period
        return context

class CabinetBillEdit(CurrentUserHotelBillAccess, AttachedFilesMixin, UpdateView):
    model = Bill
    form_class = CabinetEditBillForm
    template_name = "cabinet/bill_edit.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CabinetBillEdit, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.target.city).count()
        context['tab'] = 'bills'
        context['hotel'] = self.object.target
        context['title_line'] = _('private cabinet')
        return context

    def get_success_url(self):
        return reverse('cabinet_bills', args=[self.object.target.city.slug,self.object.target.slug])

class CabinetBookings(HotelPathMixin, CurrentUserHotelAdmin, SingleObjectMixin, ListView):
#    model = Hotel
    paginate_by = 20
    template_name = "cabinet/bookings.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        kwargs['object'] = self.object
        context = super(CabinetBookings, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.city).count()
        context['tab'] = 'booking'
        context['hotel'] = self.object
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
            return Booking.objects.filter(hotel=self.object, date__range=(from_date, to_date))
        except :
            return Booking.objects.filter(hotel=self.object)

class CabinetBills(HotelPathMixin, CurrentUserHotelAdmin, SingleObjectMixin, ListView):
#    model = Hotel
    template_name = "cabinet/bills.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        kwargs['object'] = self.object
        context = super(CabinetBills, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.city).count()
        context['tab'] = 'bills'
        context['hotel'] = self.object
        context['title_line'] = _('bills')
        return context

    def get_queryset(self):
        self.object = self.get_object()
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

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BookingsList, self).get_context_data(**kwargs)
        context['tab'] = 'bookings'
        context['title_line'] = _('booking list')
        return context

    def get_queryset(self):
        try:
            f_date = self.request.GET.get('from')
            from_date = convert_to_date(f_date)
            t_date = self.request.GET.get('to')
            to_date = convert_to_date(t_date)
            if from_date > to_date:
                from_date, to_date = to_date, from_date
            return Booking.objects.filter(date__range=(from_date, to_date))
        except :
            return Booking.objects.all()

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
        result = []
        if report_type == 'all':
            result = Hotel.objects.all()
            self.report_name = _('All hotels in system')
        elif report_type == 'notsetpayment':
            result = Hotel.objects.filter(payment_method=None)
            self.report_name = _('Hotels without payment methods')
        elif report_type == 'setpayment':
            result = Hotel.objects.exclude(payment_method=None)
            self.report_name = _('Hotels with payment methods')
        elif report_type == 'notsetadmins':
            result = Hotel.objects.filter(admins=None)
            self.report_name = _('Hotels without admins')
        elif report_type == 'setadmins':
            result = Hotel.objects.exclude(admins=None)
            self.report_name = _('Hotels with admins')
        if result:
            result = result.order_by('city__name','name')
        self.result_count = len(result)
        self.report_arg = report_type
        return result

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ReportView, self).get_context_data(**kwargs)
        context['tab'] = 'reports'
        context['title_line'] = _('site reports')
        context['report_name'] = self.report_name
        context['result_count'] = self.result_count
        context['report_arg'] = self.report_arg
        return context


class UserCabinet(CurrentUserCabinetAccess, UpdateView):
    model = Profile
    form_class = UserCabinetInfoForm
    template_name = "usercabinet/info.html"

    def get_form_kwargs(self):
        kwargs = super(UserCabinet, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_object(self, queryset=None):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return user.get_profile()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(UserCabinet, self).get_context_data(**kwargs)
        context['tab'] = 'info'
        context['title_line'] = _('private cabinet')
        return context

    def get_success_url(self):
        return reverse('user_profile', args=[self.object.user.username])

class UserBookings(CurrentUserCabinetAccess, SingleObjectMixin, ListView):
#    model = Profile
    paginate_by = 5
    template_name = "usercabinet/bookings.html"

    def get_object(self, queryset=None):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return user.get_profile()

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
            return Booking.objects.filter(user=self.object.user, date__range=(from_date, to_date))
        except :
            return Booking.objects.filter(user=self.object.user)

class UserBookingDetail(CurrentUserBookingAccess, DetailView):
    model = Booking
    slug_field = 'uuid'
    template_name = "usercabinet/booking.html"

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(UserBookingDetail, self).get_context_data(**kwargs)
        context['title_line'] = _('Booking ID')+' '+self.object.uuid
        context['tab'] = 'bookings'
        return context


class ClientBooking(RedirectHttpsView, DetailView):
    model = Hotel
    template_name = "booking/add.html"

    def get_object(self, queryset=None):
        room = get_object_or_404(Room, pk=self.kwargs['room'])
        return room.hotel

    def get_context_data(self, **kwargs):
        f_date = self.request.GET.get('from') or None
        t_date = self.request.GET.get('to') or None
        guests = guests_from_request(self.request)
        if f_date and t_date and guests and ('room' in self.kwargs.keys()):
            try:
                room_id = int(self.kwargs['room'])
            except ValueError:
                raise Http404
            room = get_object_or_404(Room,id=room_id)
            if room.hotel.payment_method.count() <1:
                raise Http404
            s = SettlementVariant.objects.filter(room=room).values_list('settlement', flat=True)
            if guests > max(s):
                raise Http404
            from_date = convert_to_date(f_date)
            to_date = convert_to_date(t_date)
            if from_date > to_date:
                f_date,t_date = t_date,f_date
                from_date,to_date = to_date,from_date
            if (from_date-datetime.now()).days < -1:
                raise Http404
            avail_count = Availability.objects.filter(room=room,
                date__range=(from_date, to_date-timedelta(days=1)),placecount__gt=0).count()
            if avail_count <> (to_date-from_date).days:
                raise Http404
            settlement = get_object_or_404(SettlementVariant,room=room,settlement=guests,enabled=True)
            valid_price_count = PlacePrice.objects.filter(settlement=settlement,
                date__range=(from_date, to_date-timedelta(days=1)),amount__gt=0).count()
            if valid_price_count <> (to_date-from_date).days:
                raise Http404
            context = super(ClientBooking, self).get_context_data(**kwargs)
            context['hotel_count'] = Hotel.objects.filter(city=self.object.city).count()
            context['tab'] = 'rates'
            context['hotel'] = self.object
            context['title_line'] = _('booking')
            context['room_id'] = room_id
            context['room'] = room
            context['settlements'] = s
            context['search_data'] = {'from_date':f_date, 'to_date':t_date, 'guests':guests}
            return context
        else :
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
                        payload = {'success': False, 'engine_error':_('Card number is wrong.')}
                        return AjaxLazyAnswer(payload)
                    else:
                        use_card = True
                        try:
                            if len(card_cvv2) <> 3:
                                raise ValueError
                            if len(card_valid) <> 5:
                                raise ValueError
                            card_cvv2 = int(card_cvv2)
                        except ValueError:
                            payload = {'success': False, 'engine_error':_('Card CVV2 is wrong.')}
                            return AjaxLazyAnswer(payload)
                else:
                    payload = {'success': False, 'engine_error':_('You enter not all data of card.')}
                    return AjaxLazyAnswer(payload)
        else:
            payload = {'success': False, 'engine_error':_('You are not select payment method.')}
            return AjaxLazyAnswer(payload)
        self.object = form.save(commit=False)
        if self.request.user.is_authenticated():
            self.object.user = self.request.user
        room = Room.objects.get(id=form.cleaned_data.get('room_id'))
        settlement = SettlementVariant.objects.get(room=room,
            settlement=form.cleaned_data.get('settlement'))
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
            price = PlacePrice.objects.get(settlement=settlement, date = on_date)
            percent = self.object.hotel.get_percent_on_date(on_date)
            commission += (price.amount*percent)/100
            all_amount += price.amount
            avail = Availability.objects.get(room=room, date = on_date)
            avail.placecount -= 1
            avail.save()
            on_date = on_date+timedelta(days=1)
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
        city = City.objects.get(slug='spb')
        result_spb = Hotel.objects.filter(city=city).count()
        city = City.objects.get(slug='moscow')
        result_moscow = Hotel.objects.filter(city=city).count()
        context['hotels_moscow'] = result_moscow
        context['hotels_spb'] = result_spb
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
        context['title_line'] = _('Booking ID')+' '+self.object.uuid
        context['tab'] = 'booking'
        return context

class BookingAdminDetail(CurrentUserSuperuser, DetailView):
    model = Booking
    slug_field = 'uuid'
    template_name = "sysadm/booking.html"

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(BookingAdminDetail, self).get_context_data(**kwargs)
        context['title_line'] = _('Booking ID')+' '+self.object.uuid
        context['tab'] = 'bookings'
        return context
