from django.views.generic.list import ListView
from nnmware.apps.money.models import Account

class AccountsList(ListView):
    model = Account
    template_name = "sysadm/accounts.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(AccountsList, self).get_context_data(**kwargs)
        context['tab'] = 'accounts'
        return context
