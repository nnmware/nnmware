from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
admin.autodiscover()

admin.site.site_header = 'Nnmware engine@2012-2020'

# NNMWARE SITE URL MAPPING 
urlpatterns = [
    url(r'^admin/', admin.site.urls),
]

urlpatterns += staticfiles_urlpatterns()
