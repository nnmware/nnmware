# nnmware(c)2012-2021

from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TransportAppConfig(AppConfig):
    name = "nnmware.apps.transport"
    verbose_name = _("Transport module")
