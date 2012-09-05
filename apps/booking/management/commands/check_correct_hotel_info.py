# -*- coding: utf-8 -*-
from datetime import timedelta, datetime
from django.utils.translation import ugettext_lazy as _

from django.core.management.base import BaseCommand
from nnmware.apps.booking.models import Hotel, Availability, SettlementVariant

class Command(BaseCommand):
    help = 'Check correct info in hotel cabinet'

    def handle(self, *args, **options):
        for hotel in Hotel.objects.all():
            result = []
            for room in hotel.room_set.all():
                avail = Availability.objects.filter(room=room,date__range=(datetime.now(), datetime.now()+timedelta(days=13))).count()
                if avail < 14:
                    avail_err = [room.get_name, _('Not completed availability')]
                    result.append(avail_err)
#                    print avail, room.get_name
                for settlement in SettlementVariant.objects.filter(room=room, enabled=True):
                    if settlement.current_amount() is 0:
                        settlement_err = [room.get_name,_('Not completed price for %s settlement') % settlement.settlement  ]
                        result.append(settlement_err)
#                        print settlement.room.get_name, settlement.settlement
                if len(result) > 0:
                    for item in result:
                        print item[0], item[1]
