from django.http import HttpResponse
from django.utils import simplejson
from nnmware.core.http import LazyEncoder

def room_rate(request):
    price = request.REQUEST['link']
    payload = {'success': False}
    return HttpResponse(simplejson.dumps(payload, cls=LazyEncoder), content_type='application/json')
