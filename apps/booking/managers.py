from django.db.models.manager import Manager

class SettlementVariantManager(Manager):

    def get_query_set(self):
        return super(SettlementVariantManager, self).get_query_set().filter(enabled=True).order_by('settlement')
