# -*- encoding: utf-8 -*-

from django.conf.urls import *

from nnmware.apps.captcha import views

urlpatterns = patterns('',
    url(r'^(?P<captcha_id>\w+)/$', views.captcha_image, name='captcha_image'),
)
