from django.conf.urls import *
from nnmware.apps.video.views import *

urlpatterns = patterns('',

    url(r'^$', VideoTimelineFeed.as_view(), name="video_timeline"),
    url(r'^popular/$', VideoPopularFeed.as_view(), name="video_popular"),
    url(r'^loved/$', VideoLovedFeed.as_view(), name="video_loved"),
    url(r'^add/$', VideoAdd.as_view(), name="video_add"),
    url(r'^latest/$', VideoLatestFeed.as_view(), name="video_latest"),
)
