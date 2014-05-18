from django.conf.urls import *
from nnmware.core import feeds
from nnmware.core.views import *

urlpatterns = patterns('',
    ### Comments ###
    #    url(r'^comment/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<parent_id>\d+)/$', NnmcommentAdd.as_view(), name="jcomment_parent_add"),
    url(r'^comment/(?P<content_type>\d+)/(?P<object_id>\d+)/add/$', NnmcommentAdd.as_view(), name="jcomment_add"),
    url(r'^comment/(?P<content_type>\d+)/(?P<object_id>\d+)/(?P<parent_id>\d+)/$', NnmcommentAdd.as_view(),
        name="jcomment_parent_add"),
    url(r'^comment/edit/(?P<pk>[0-9]+)/$', NnmcommentEdit.as_view(), name="jcomment_edit"),
    url(r'^comment/edit_editor/(?P<pk>[0-9]+)/$', NnmcommentEditorEdit.as_view(), name="jcomment_edit_editor"),
    url(r'^comment/edit_admin/(?P<pk>[0-9]+)/$', NnmcommentAdminEdit.as_view(), name="jcomment_edit_admin"),
    url(r'^comment/status/(?P<pk>[0-9]+)/$', NnmcommentStatus.as_view(), name="jcomment_status"),
    url(r'^comment/status_editor/(?P<pk>[0-9]+)/$', NnmcommentEditorStatus.as_view(), name="jcomment_status_editor"),
    url(r'^comment/status_admin/(?P<pk>[0-9]+)/$', NnmcommentAdminStatus.as_view(), name="jcomment_status_admin"),
    url(r'^pic/add/$', AddPicView.as_view(), name="pic_add"),
    url(r'^doc/add/$', DocAdd.as_view(), name="doc_add"),
    url(r'^doc/delete/(?P<pk>[0-9]+)/$', DocDelete.as_view(), name="doc_del"),
    url(r'^pic/delete/(?P<pk>[0-9]+)/$', PicDelete.as_view(), name="pic_del"),
    url(r'^pic/view/(?P<pk>[0-9]+)/$', PicView.as_view(), name="pic_view"),
    url(r'^pic/editor/(?P<pk>[0-9]+)/$', PicEditor.as_view(), name="pic_editor"),
    url(r'^doc/edit/(?P<pk>\d+)/$', DocEdit.as_view(), name="doc_edit"),
    url(r'^settings/$', UserSettings.as_view(), name='user_settings'),
    url(r'^signin/$', LoginView.as_view(), name="signin"),
    url(r'^signup/$', SignupView.as_view(), name="signup"),
    url(r'^logout/$', LogoutView.as_view(), name="logout"),
    url(r'^tags/popular/$', TagsPopularView.as_view(), name="tags_popular"),
    url(r'^tags/cloud/$', TagsCloudView.as_view(), name="tags_cloud"),
    url(r'^tags/$', TagsView.as_view(), name="tags"),
    url(r'^tags/(?P<letter>[a-zA-Z0-9-])/$', TagsLetterView.as_view(), name="tags_letter"),
    url(r'^tag/(?P<slug>[a-zA-Z0-9-]+)/$', TagDetail.as_view(), name='tag_detail'),
)


urlpatterns += patterns('',
    # Syndication Feeds
    url(r'^feed/(?P<content_type_id>\d+)/(?P<object_id>\d+)/atom/$',
        feeds.AtomObjectActivityFeed(), name='actstream_object_feed_atom'),
    url(r'^feed/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$',
        feeds.ObjectActivityFeed(), name='actstream_object_feed'),
    url(r'^feed/(?P<content_type_id>\d+)/atom/$',
        feeds.AtomModelActivityFeed(), name='actstream_model_feed_atom'),
    url(r'^feed/(?P<content_type_id>\d+)/(?P<object_id>\d+)/as/$',
        feeds.ActivityStreamsObjectActivityFeed(),
        name='actstream_object_feed_as'),
    url(r'^feed/(?P<content_type_id>\d+)/$',
        feeds.ModelActivityFeed(), name='actstream_model_feed'),
    url(r'^feed/$', feeds.UserActivityFeed(), name='actstream_feed'),
    url(r'^feed/atom/$', feeds.AtomUserActivityFeed(),
        name='actstream_feed_atom'),

    # Follower and Actor lists
#    url(r'^followers/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$',
#        followers, name='actstream_followers'),
#    url(r'^actors/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$',
#        actor, name='actstream_actor'),
#    url(r'^actors/(?P<content_type_id>\d+)/$',
#        model, name='actstream_model'),

#    url(r'^detail/(?P<action_id>\d+)/$', detail, name='actstream_detail'),
#    url(r'^notice/$', NoticeView.as_view(), name='actstream_notice'),
#    url(r'^notice/(?P<username>[-\w]+)/$', user, name='actstream_user'),
#    url(r'^$', stream, name='actstream'),

)
