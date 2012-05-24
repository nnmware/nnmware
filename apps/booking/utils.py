# -*- coding: utf-8 -*-

def guests_from_get_request(request):
    guests_get = request.GET.get('guests') or None
    if guests_get:
        guests = int(guests_get)
    else:
        guests = None
    return guests
