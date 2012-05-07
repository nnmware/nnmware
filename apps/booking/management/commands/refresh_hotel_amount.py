from django.core.management.base import BaseCommand, CommandError
from nnmware.apps.booking.models import Hotel

class Command(BaseCommand):
    help = 'Recalculate current minimal hotel amount'

    def handle(self, *args, **options):
        for hotel in Hotel.objects.all():
            hotel.update_hotel_amount()
