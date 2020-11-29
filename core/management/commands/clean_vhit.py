# nnmware(c)2012-2020

from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from nnmware.core.models import VisitorHit


class Command(BaseCommand):

    def handle(self, *args, **options):
        time_threshold = datetime.now() - timedelta(days=10)
        VisitorHit.objects.filter(date__lt=time_threshold).delete()
