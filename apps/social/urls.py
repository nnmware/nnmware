"""URLs module"""
from django.conf.urls import patterns, url

from nnmware.apps.social.views import auth, complete, disconnect

urlpatterns = patterns('',
    # authentication
    url(r'^login/(?P<backend>[^/]+)/$', auth, name='socialauth_begin'),
    url(r'^complete/(?P<backend>[^/]+)/$', complete, name='socialauth_complete'),
    # disconnection
    url(r'^disconnect/(?P<backend>[^/]+)/$', disconnect, name='socialauth_disconnect'),
    url(r'^disconnect/(?P<backend>[^/]+)/(?P<association_id>[^/]+)/$', disconnect, name='socialauth_disconnect_individual'),
)
