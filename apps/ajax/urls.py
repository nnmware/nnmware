from django.conf.urls import *

from nnmware.apps.ajax.views import *

urlpatterns = patterns('',
    url(r'^users/list/$', autocomplete_users, name='autocomplete_users'),
    url(r'^tags/list/$', autocomplete_tags, name='autocomplete_tags'),
    url(r'^video/like/(?P<object_id>\d+)/$', video_like, name='video_like'),
    url(r'^video/dislike/(?P<object_id>\d+)/$', video_dislike, name='video_dislike'),
    url(r'^follow/tag/(?P<object_id>\d+)/$', follow_tag, name='follow_tag'),
    url(r'^unfollow/tag/(?P<object_id>\d+)/$', unfollow_tag, name='unfollow_tag'),
    url(r'^follow/user/(?P<object_id>\d+)/$', follow_user, name='follow_user'),
    url(r'^unfollow/user/(?P<object_id>\d+)/$', unfollow_user, name='unfollow_user'),
    url(r'^video/$', get_video, name='get_video'),
    url(r'^doc/(?P<content_type>\d+)/(?P<object_id>\d+)/$', doc_uploader,
        name="doc_ajax"),
    url(r'^pic/(?P<content_type>\d+)/(?P<object_id>\d+)/$', pic_uploader,
        name="pic_ajax"),
    # Follow/Unfollow API
    url(r'^follow/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$', follow_object, name='follow'),
    url(r'^unfollow/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$', unfollow_object, name='unfollow'),
)
