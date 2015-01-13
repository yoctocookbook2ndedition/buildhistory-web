# buildhistory-web - top-level URL definitions
#
# Based on the Django project template
#
# Copyright (c) Django Software Foundation and individual contributors.
# All rights reserved.

from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^warningmgr/', include('warningmgr.urls')),
    #override the default urls
    url(r'^password/change/$',
                auth_views.password_change,
                name='password_change'),
    url(r'^password/change/done/$',
                auth_views.password_change_done,
                name='password_change_done'),
    url(r'^password/reset/$',
                auth_views.password_reset,
                name='password_reset'),
    url(r'^password/reset/done/$',
                auth_views.password_reset_done,
                name='password_reset_done'),
    url(r'^password/reset/complete/$',
                auth_views.password_reset_complete,
                name='password_reset_complete'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
                auth_views.password_reset_confirm,
                name='password_reset_confirm'),

    #and now add the registration urls
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'.*', RedirectView.as_view(url='/warningmgr/'))
)

