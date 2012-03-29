from django.db.models.query_utils import Q
from django.http import HttpResponse
from django.utils import simplejson
from nnmware.apps.address.models import City
from nnmware.core.http import LazyEncoder


def autocomplete_city(request):
    search_qs = City.objects.filter(
        Q(name__icontains=request.REQUEST['q']) |
        Q(name_en__icontains=request.REQUEST['q'])).order_by('name')

    results = []
    for r in search_qs:
        results.append(r.name)
    payload = {'q': results}
    return HttpResponse(simplejson.dumps(payload, cls=LazyEncoder), content_type='application/json')
