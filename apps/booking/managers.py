# nnmware(c)2012-2016

from __future__ import unicode_literals

from django.db.models.manager import Manager


class SettlementVariantManager(Manager):

    def get_queryset(self):
        return super(SettlementVariantManager, self).get_queryset().filter(enabled=True).order_by('settlement')
