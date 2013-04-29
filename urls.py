# buildhistory-web - top-level URL definitions
#
# Based on the Django project template
#
# Copyright (c) Django Software Foundation and individual contributors.
# All rights reserved.

from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import redirect_to

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^warningmgr/', include('warningmgr.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'.*', redirect_to, {'url' : '/warningmgr/'})
)

