# -*- coding: utf-8 -*-
from datetime import timedelta, datetime

from django.core.management.base import BaseCommand
from nnmware.apps.booking.models import Hotel, Availability

class Command(BaseCommand):
    help = 'Check correct info in hotel cabinet'

    def handle(self, *args, **options):
        for hotel in Hotel.objects.all():
            for room in hotel.room_set.all():
                avail = Availability.objects.filter(room=room,date__range=(datetime.now(), datetime.now()+timedelta(days=13))).count()
                if avail < 14:
                    print avail, room.get_name

