# nnmware(c)2012-2020

from __future__ import unicode_literals

from django.conf.urls import *

from nnmware.apps.publication.views import *

urlpatterns = [
    url(r'^search/$', PublicationSearch.as_view(), name='articles_search'),
    url(r'^$', PublicationList.as_view(), name="article_index"),
    url(r'^my/$', PublicationMyList.as_view(), name="article_my"),
    url(r'^locked/$', PublicationLockedList.as_view(), name="article_locked"),
    url(r'^new/$', PublicationList.as_view(), name="article_new"),
    url(r'^updated/$', PublicationUpdatedList.as_view(), name="article_updated"),
    url(r'^popular/$', PublicationPopularList.as_view(), name="article_popular"),
    url(r'^moderation/$', PublicationModerationList.as_view(), name="article_moderation"),
    url(r'^deleted/$', PublicationDeletedList.as_view(), name="article_deleted"),
    url(r'^add/$', PublicationAdd.as_view(), name="article_add"),
    url(r'^edit/(?P<pk>[0-9]+)/$', PublicationEdit.as_view(), name="article_edit"),
    url(r'^edit_editor/(?P<pk>[0-9]+)/$', PublicationEditEditor.as_view(), name="article_edit_editor"),
    url(r'^edit_admin/(?P<pk>[0-9]+)/$', PublicationEditAdmin.as_view(), name="article_edit_admin"),
    url(r'^status/(?P<pk>[0-9]+)/$', PublicationStatus.as_view(), name="article_status"),
    url(r'^status_editor/(?P<pk>[0-9]+)/$', PublicationStatusEditor.as_view(), name="article_status_editor"),
    url(r'^status_admin/(?P<pk>[0-9]+)/$', PublicationStatusAdmin.as_view(), name="article_status_admin"),
    url(r'^category/$', PublicationList.as_view()),
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/(?P<slug>.*)/$', PublicationDetail.as_view(),
        name='article_detail'),
    url(r'^(?P<year>\d{4})/$', PublicationYearList.as_view(), name='article_year'),
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/$', PublicationMonthList.as_view(), name='article_month'),
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/$', PublicationDayList.as_view(), name='article_day'),
    url(r'^author/(?P<username>.*)/$', PublicationAuthor.as_view(), name='articles_by_author'),
    url(r'^category/(?P<parent_slugs>[-\w]+/)*(?P<slug>[-\w]+)/$', PublicationCategory.as_view(),
        name='articles_category'),
]
