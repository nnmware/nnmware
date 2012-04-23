# -*- coding: utf-8 -*-
from datetime import date, timedelta, datetime
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic.base import View, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView, CreateView
from django.views.generic.list import ListView
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.booking.models import *
from nnmware.apps.booking.forms import *
from nnmware.apps.userprofile.models import Profile
from nnmware.core.views import AttachedImagesMixin, AttachedFilesMixin, AjaxFormMixin
from nnmware.apps.money.models import Account
import time
from nnmware.core.utils import date_range, convert_to_date

class HotelList(ListView):
    model = Hotel
    template_name = "hotels/list.html"

    def get_queryset(self):
        order = self.request.GET.get('order') or None
        if order:
            if order == 'name':
                result = Hotel.objects.order_by('name')
                tab = 'name'
            elif order == 'class':
                result = Hotel.objects.order_by('-starcount')
                tab = 'class'
            elif order == 'amount':
                result = Hotel.objects.order_by('starcount')
                tab = 'amount'
            elif order == 'review':
                result = Hotel.objects.order_by('-point')
                tab = 'review'
            else:
                pass
        else:
            result = Hotel.objects.all()
            tab = 'name'
        self.tab_title = tab
        return result

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(HotelList, self).get_context_data(**kwargs)
        context['title_line'] = _('list of hotels')
        context['tourism_list'] = context['object_list'][0].tourism.all
        context['tab'] = self.tab_title
        context['api_key'] = settings.YANDEX_MAPS_API_KEY
        return context

class HotelInCity(ListView):
    model = Hotel
    template_name = "hotels/list.html"

    def get_queryset(self):
        city = City.objects.get(slug=self.kwargs['slug'])
        return Hotel.objects.filter(city=city)

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(HotelInCity, self).get_context_data(**kwargs)
        context['title_line'] = _('list of hotels')
        context['tab'] = 'name'
        context['api_key'] = settings.YANDEX_MAPS_API_KEY
        return context


class HotelAdminList(ListView):
    model = Hotel
    template_name = "hotels/list.html"

    def get_queryset(self):
        result = Hotel.objects.all() #filter(admins__user = self.request.user)
        return result

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(HotelAdminList, self).get_context_data(**kwargs)
        context['title_line'] = _('list of hotels')
        context['tab'] = _('admin of hotels')
        context['api_key'] = settings.YANDEX_MAPS_API_KEY
        return context


class HotelDetail(AttachedImagesMixin, DetailView):
    model = Hotel
    slug_field = 'slug'
    template_name = "hotels/detail.html"

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(HotelDetail, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.city).count()
        context['tab'] = 'description'
        context['title_line'] = self.object.get_name
        try:
            f_date = self.request.GET.get('from')
            from_date = convert_to_date(f_date)
            t_date = self.request.GET.get('to')
            to_date = convert_to_date(t_date)
            if from_date > to_date:
                from_date, to_date = to_date, from_date
            place_need = self.request.GET.get('placecount')
            context['free_room'] = self.object.free_room(from_date,to_date,place_need)
            context['search'] = 1
            context['from'] = f_date
            context['to'] = t_date
            context['placecount'] = place_need
        except :
            pass
        return context

class HotelLocation(DetailView):
    model = Hotel
    slug_field = 'slug'
    template_name = "hotels/location.html"

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(HotelLocation, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.city).count()
        context['tourism_list'] = self.object.tourism.all
        context['title_line'] = self.object.get_name
        context['tab'] = 'location'
        context['api_key'] = settings.YANDEX_MAPS_API_KEY
        return context

class HotelReviews(DetailView):
    model = Hotel
    slug_field = 'slug'
    template_name = "hotels/reviews.html"

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(HotelReviews, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.city).count()
        context['tab'] = 'reviews'
        context['title_line'] = self.object.get_name
        context['reviews'] = self.object.review_set.all()
        return context


class CabinetInfo(AttachedImagesMixin, UpdateView):
    model = Hotel
    form_class = CabinetInfoForm
    template_name = "cabinet/info.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CabinetInfo, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.city).count()
        context['options_list'] = HotelOption.objects.order_by('category')
        context['tab'] = 'common'
        context['title_line'] = _('private cabinet')
        return context

    def get_success_url(self):
        return reverse('cabinet_info', args=[self.object.pk])

class CabinetRooms(CreateView):
    model = Room
    form_class = CabinetAddRoomForm
    template_name = "cabinet/rooms.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        hotel = get_object_or_404(Hotel, id=self.kwargs['pk'])
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
        # Call the base implementation first to get a context
        context = super(CabinetRooms, self).get_context_data(**kwargs)
        hotel = get_object_or_404(Hotel, id=self.kwargs['pk'])
        context['hotel_count'] = Hotel.objects.filter(city=hotel.city).count()
        context['options_list'] = RoomOption.objects.order_by('category')
        context['tab'] = 'rooms'
        context['hotel'] = hotel
        return context

    def get_success_url(self):
            return reverse('cabinet_rooms', args=[self.object.hotel.pk])

class CabinetEditRoom(AttachedImagesMixin, UpdateView):
    model = Room
    form_class = CabinetEditRoomForm
    template_name = "cabinet/room.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CabinetEditRoom, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.hotel.city).count()
        context['options_list'] = RoomOption.objects.order_by('category')
        context['tab'] = 'rooms'
        context['hotel'] = self.object.hotel
        return context

    def get_success_url(self):
        return reverse('cabinet_rooms', args=[self.object.hotel.pk])

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


class CabinetRates(DetailView):
    model = Hotel
    template_name = "cabinet/rates.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CabinetRates, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.city).count()
        context['tab'] = 'rates'
        context['hotel'] = self.object
        context['title_line'] = _('private cabinet')
        if 'room' in self.kwargs.keys():
            context['room_id'] = int(self.kwargs['room'])
        else:
            context['room_id'] = Room.objects.filter(hotel=self.object)[0].id
        try:
            f_date = self.request.GET.get('from')
            from_date = datetime.fromtimestamp(time.mktime(time.strptime(f_date, "%d.%m.%Y")))
            t_date = self.request.GET.get('to')
            to_date = datetime.fromtimestamp(time.mktime(time.strptime(t_date, "%d.%m.%Y")))
            if from_date > to_date:
                from_date, to_date = to_date, from_date
            context['dates'] = date_range(from_date, to_date)
        except :
            context['dates'] = [datetime.today()]
        return context

class CabinetBillEdit(AttachedFilesMixin, UpdateView):
    model = Account
    form_class = CabinetEditBillForm
    template_name = "cabinet/bill_edit.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CabinetBillEdit, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.target.city).count()
        context['tab'] = 'bills'
        context['hotel'] = self.object.target
        return context

    def get_success_url(self):
        return reverse('cabinet_bills', args=[self.object.target.pk])

class CabinetBookings(DetailView):
    model = Hotel
    template_name = "cabinet/bookings.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CabinetBookings, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.city).count()
        context['tab'] = 'booking'
        context['hotel'] = self.object
        context['bookings'] = Booking.objects.filter(hotel=self.object)
        context['title_line'] = _('bookings')
        return context

class CabinetBills(DetailView):
    model = Hotel
    template_name = "cabinet/bills.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CabinetBills, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.city).count()
        context['tab'] = 'bills'
        context['hotel'] = self.object
        context['accounts'] = Account.objects.for_object(self.object)
        context['title_line'] = _('bills')
        return context

class RequestAddHotelView(CreateView):
    model = RequestAddHotel
    form_class = RequestAddHotelForm
    template_name = "requests/add.html"

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
        return super(RequestAddHotelView, self).form_valid(form)



class BookingsList(ListView):
    model = Booking
    template_name = "sysadm/bookings.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BookingsList, self).get_context_data(**kwargs)
        context['tab'] = 'bookings'
        context['title_line'] = _('booking list')
        return context

class RequestsList(ListView):
    model = RequestAddHotel
    template_name = "sysadm/requests.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(RequestsList, self).get_context_data(**kwargs)
        context['tab'] = 'requests'
        context['title_line'] = _('request for add')
        return context

class UserCabinet(UpdateView):
    model = Profile
    form_class = UserCabinetInfoForm
    template_name = "usercabinet/info.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(UserCabinet, self).get_context_data(**kwargs)
        context['tab'] = 'info'
        context['title_line'] = _('private cabinet')
        return context

    def get_success_url(self):
        return reverse('user_profile', args=[self.object.pk])

class ClientBooking(DetailView):
    model = Hotel
    template_name = "booking/add.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ClientBooking, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.city).count()
        context['tab'] = 'rates'
        context['hotel'] = self.object
        context['title_line'] = _('booking')
        if 'room' in self.kwargs.keys():
            context['room_id'] = int(self.kwargs['room'])
            room = Room.objects.get(id=int(self.kwargs['room']))
            context['room'] = room
            context['settlements'] = \
                SettlementVariant.objects.filter(room=room).values_list('settlement', flat=True)
        try:
            f_date = self.request.GET.get('from')
            from_date = convert_to_date(f_date)
            t_date = self.request.GET.get('to')
            to_date = convert_to_date(t_date)
            if from_date > to_date:
                from_date, to_date = to_date, from_date
            place_need = self.request.GET.get('placecount')
            context['from'] = f_date
            context['to'] = t_date
            context['placecount'] = place_need
        except :
            pass
        return context

class ClientAddBooking(AjaxFormMixin, CreateView):
    model = Booking
    form_class = BookingAddForm

    def get_success_url(self):
        return reverse('hotel_list')

    def form_valid(self, form):
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
        all_amount = 0
        on_date = from_date
        while on_date < to_date:
            price = PlacePrice.objects.get(settlement=settlement, date = on_date)
            all_amount +=int(price.amount)
            avail = Availability.objects.get(room=room, date = on_date)
            avail.placecount -= 1
            avail.save()
            on_date = on_date+timedelta(days=1)
        self.object.amount = all_amount
        self.object.currency = price.currency
        self.ip = self.request.META['REMOTE_ADDR']
        self.user_agent = self.request.META['HTTP_USER_AGENT']
        self.object.save()
        return super(ClientAddBooking, self).form_valid(form)

class RequestAdminAdd(TemplateView):
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
    