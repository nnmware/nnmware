# -*- coding: utf-8 -*-

from django.http import HttpResponse
from nnmware.apps.captcha import render


def captcha_image(request, captcha_id):
    response = HttpResponse(mimetype='image/jpeg')
    render(captcha_id, response)
    return response
