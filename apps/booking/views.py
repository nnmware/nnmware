# -*- coding: utf-8 -*-
from datetime import date, timedelta
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView, CreateView
from django.views.generic.list import ListView
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.booking.models import *
from nnmware.apps.booking.forms import *
from nnmware.core.views import AttachedImagesMixin
from nnmware.apps.booking.models import RequestAddHotel
from nnmware.apps.booking.forms import RequestAddHotelForm

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
                result = Hotel.objects.order_by('point')
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
        context['tab'] = self.tab_title
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
        return context

class HotelLocation(DetailView):
    model = Hotel
    slug_field = 'slug'
    template_name = "hotels/location.html"

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(HotelLocation, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.city).count()
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


class CabinetRates(DetailView):
    model = Hotel
    template_name = "cabinet/rates.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CabinetRates, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.city).count()
        context['tab'] = 'rates'
        context['hotel'] = self.object
        return context


class CabinetRoomRates(DetailView):
    model = Room
    template_name = "cabinet/room_rates.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CabinetRoomRates, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.hotel.city).count()
        context['tab'] = 'rates'
        context['hotel'] = self.object.hotel
        try:
            from_date = self.request.GET.get('from')
            to_date = self.request.GET.get('to')
            context['date_range'] = range(from_date, to_date)
        except :
            base = datetime.today()
            dateList = [ base + timedelta(days=x) for x in range(0,31) ]
            context['date_range'] = dateList
        return context

class CabinetBookings(DetailView):
    model = Hotel
    template_name = "cabinet/bookings.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CabinetBookings, self).get_context_data(**kwargs)
        context['hotel_count'] = Hotel.objects.filter(city=self.object.city).count()
        context['tab'] = 'booking'
        context['hotel'] = self.object
        context['bookings'] = Booking.objects.filter(room__hotel=self.object)
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
        return context

class RequestAddHotelView(CreateView):
    model = RequestAddHotel
    form_class = RequestAddHotelForm
    template_name = "requests/add.html"

    def get_success_url(self):
        return reverse('hotel_list')