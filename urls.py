from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
admin.autodiscover()

# NNMWARE SITE URL MAPPING 
urlpatterns = ['',
    url(r'^admin/grappelli/', include('grappelli.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
]

urlpatterns += staticfiles_urlpatterns()
