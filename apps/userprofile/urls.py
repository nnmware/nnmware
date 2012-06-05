# -*- encoding: utf-8 -*-

from django.conf.urls import *
from django.views.generic.base import TemplateView
from nnmware.apps.userprofile.views import *


urlpatterns = patterns(
    '',
    url(r'^$', UserList.as_view(), name='users'),
    url(r'^men/$', UserMenList.as_view(), name='men'),
    url(r'^women/$', UserWomenList.as_view(), name='women'),
    url(r'^search/$', UserSearch.as_view(), name='user_search'),

    #    url(r'^register/complete/$', direct_to_template, {'template':
    # 'userprofile/userprofile/registration_done.html'},name='signup_complete'),
#    url(r'^email/validation/(?P<key>.{70})/$', email_validation_process,
#        name='email_validation_process'),

    #    url(r'^email/validation/processed/$', direct_to_template,
    #        {'template': 'userprofile/userprofile/email_validation_processed.html'},
    #        name='email_validation_processed'),
    url(r'^password/reset/$', 'django.contrib.auth.views.password_reset', {'template_name': 'profile/userprofile/password_reset.html',
             'email_template_name': 'userprofile/email/password_reset_email.txt'},
        name='password_reset'),
    url(r'^password/reset/done/$',
        'django.contrib.auth.views.password_reset_done',
            {'template_name': 'profile/userprofile/password_reset_done.html'},
        name='password_reset_done'),
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'django.contrib.auth.views.password_reset_confirm',
            {'template_name': 'profile/userprofile/password_reset_confirm.html'},
        name="password_reset_confirm"),
    url(r'^(?P<year>\d{4})/$', UserYearList.as_view(), name='user_year'),
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/$', UserMonthList.as_view(),
        name='user_month'),
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/$',
        UserDayList.as_view(), name='user_day'),

)
