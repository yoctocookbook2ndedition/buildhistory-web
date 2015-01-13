# buildhistory-web - URL definitions
#
# Copyright (C) 2013-2015 Intel Corporation
#
# Licensed under the MIT license, see COPYING.MIT for details

from django.conf.urls import *
from django.views.generic import DetailView, ListView
from warningmgr.models import WarningItem
from warningmgr.views import WarningListView, ReviewedWarningListView

urlpatterns = patterns('',
    url(r'^$',
        WarningListView.as_view(
            template_name='warningmgr/index.html'),
            name='warning_list'),
    url(r'^reviewed/$',
        ReviewedWarningListView.as_view(
            template_name='warningmgr/index.html'),
            name='warning_list_reviewed'),
    url(r'^multi_action/$', 'warningmgr.views.multi_action', name='multi_action'),
    url(r'^warning/(?P<pk>\d+)/$',
        DetailView.as_view(
            model=WarningItem,
            template_name='warningmgr/detail.html'),
            name='warning_item'),
    url(r'^warning/(?P<pk>\d+)/postcomment/$', 'warningmgr.views.postcomment', name='postcomment'),
    url(r'^warning/(?P<pk>\d+)/ignore/$', 'warningmgr.views.ignore', name="ignore"),
    url(r'^warning/(?P<pk>\d+)/actionreq/$', 'warningmgr.views.actionreq', name="actionreq"),
    url(r'^warning/(?P<pk>\d+)/resolve/$', 'warningmgr.views.resolve', name="resolve"),
    url(r'^warning/(?P<pk>\d+)/unreview/$', 'warningmgr.views.unreview', name="unreview"),
)
