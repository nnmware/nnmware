# nnmware(c)2012-2021

from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PublicationAppConfig(AppConfig):
    name = "nnmware.apps.publication"
    verbose_name = _("Publication module")
