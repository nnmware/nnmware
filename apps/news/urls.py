# -*- coding: utf-8 -*-
# nnmware(c)2012-2016
# News urls

from __future__ import unicode_literals

from django.conf.urls import url

from nnmware.apps.topic.views import *

urlpatterns = [
    url(r'^search/$', TopicSearch.as_view(), name='topic_search'),
    url(r'^$', TopicList.as_view(), name="topic_index"),
    url(r'^my/$', TopicUserList.as_view(), name="topic_my"),
    url(r'^new/$', TopicList.as_view(), name="topic_new"),
    url(r'^updated/$', TopicUpdatedList.as_view(), name="topic_updated"),
    url(r'^popular/$', TopicPopularList.as_view(), name="topic_popular"),
    url(r'^moderation/$', TopicModerationList.as_view(), name="topic_moderation"),
    url(r'^deleted/$', TopicDeletedList.as_view(), name="topic_deleted"),
    url(r'^locked/$', TopicLockedList.as_view(), name="topic_locked"),
    url(r'^add/$', TopicAdd.as_view(), name="topic_add"),
    url(r'^edit/(?P<pk>[0-9]+)/$', TopicEdit.as_view(), name="topic_edit"),
    url(r'^edit_editor/(?P<pk>[0-9]+)/$', TopicEditorEdit.as_view(), name="topic_edit_editor"),
    url(r'^edit_admin/(?P<pk>[0-9]+)/$', TopicAdminEdit.as_view(), name="topic_edit_admin"),
    url(r'^status/(?P<pk>[0-9]+)/$', TopicStatus.as_view(), name="topic_status"),
    url(r'^status_editor/(?P<pk>[0-9]+)/$', TopicEditorStatus.as_view(), name="topic_status_editor"),
    url(r'^status_admin/(?P<pk>[0-9]+)/$', TopicAdminStatus.as_view(), name="topic_status_admin"),
    url(r'^(?P<year>\d{4})/$', TopicYearList.as_view(), name="topic_year"),
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/$', TopicMonthList.as_view(), name="topic_month"),
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/$', TopicDayList.as_view(), name="topic_day"),
    url(r'^category/(?P<parent_slugs>[-\w]+/)*(?P<slug>[-\w]+)/$', TopicCategory.as_view(), name="topic_category"),
    url(r'^id/(?P<pk>[0-9]+)/$', TopicDetail.as_view(), name="topic_one"),
]
