from django.db.models.manager import Manager


class SettlementVariantManager(Manager):

    def get_queryset(self):
        return super(SettlementVariantManager, self).get_queryset().filter(enabled=True).order_by('settlement')
