# nnmware(c)2012-2016

from django.core.management.base import BaseCommand

from nnmware.apps.booking.models import Hotel


class Command(BaseCommand):
    help = 'Recalculate current minimal hotel amount'

    def handle(self, *args, **options):
        for hotel in Hotel.objects.all():
            hotel.update_hotel_amount()
