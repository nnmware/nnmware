# nnmware(c)2012-2020

from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import gettext as _


class DossierAppConfig(AppConfig):
    name = "nnmware.apps.dossier"
    verbose_name = _("Dossier module")
