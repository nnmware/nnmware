# -*- coding: utf-8 -*-
from datetime import timedelta, datetime
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.translation import activate

from django.core.management.base import BaseCommand
from nnmware.apps.booking.models import Hotel, Availability, SettlementVariant
from nnmware.core.utils import send_template_mail

class Command(BaseCommand):
    help = 'Check correct info in hotel cabinet'

    def handle(self, *args, **options):
        activate('ru')
        for hotel in Hotel.objects.all():
            result = []
            for room in hotel.room_set.all():
                avail = Availability.objects.filter(room=room,date__range=(datetime.now(), datetime.now()+timedelta(days=13))).count()
                if avail < 14:
                    avail_err = [room.get_name, _('Not filled availability')]
                    result.append(avail_err)
                for settlement in SettlementVariant.objects.filter(room=room, enabled=True):
                    if settlement.current_amount() is 0:
                        settlement_err = [room.get_name,_('Not filled price for %s-placed settlement') % settlement.settlement  ]
                        result.append(settlement_err)
            if len(result) > 0:
                recipients = settings.BOOKING_MANAGERS
                mail_dict = {'hotel': hotel, 'site_name': settings.SITENAME,'items':result}
                subject = 'booking/err_hotel_subject.txt'
                body = 'booking/err_hotel.txt'
                send_template_mail(subject,body,mail_dict,recipients)
#
#        for item in result:
#                    print item[0], item[1]
