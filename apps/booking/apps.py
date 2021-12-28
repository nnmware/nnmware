# nnmware(c)2012-2020

from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import gettext as _


class BookingAppConfig(AppConfig):
    name = "nnmware.apps.booking"
    verbose_name = _("Booking module")
