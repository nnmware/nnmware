# nnmware(c)2012-2017

from __future__ import unicode_literals

from django.views.generic.list import ListView

from nnmware.apps.money.models import Bill


class BillsList(ListView):
    model = Bill
    paginate_by = 20
    template_name = "sysadm/bills.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BillsList, self).get_context_data(**kwargs)
        context['tab'] = 'bills'
        return context
