from django.db.models.manager import Manager

class SettlementVariantManager(Manager):
    """
     A ``Manager`` which borrows all of the same methods from ``ThreadedCommentManager``,
     but which also restricts the queryset to only the published methods
     (in other words, ``is_public = True``).
     """

    def get_query_set(self):
        return super(SettlementVariantManager, self).get_query_set().filter(enabled=True).order_by('settlement')
