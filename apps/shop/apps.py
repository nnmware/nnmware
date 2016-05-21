# nnmware(c)2012-2016

from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ShopAppConfig(AppConfig):
    name = "nnmware.apps.shop"
    verbose_name = _("Shop module")
