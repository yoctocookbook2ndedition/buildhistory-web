# buildhistory-web - admin interface definitions
#
# Copyright (C) 2013-2015 Intel Corporation
#
# Licensed under the MIT license, see COPYING.MIT for details

from warningmgr.models import Build, WarningItem, Comment
from django.contrib import admin

admin.site.register(Build)
admin.site.register(WarningItem)
admin.site.register(Comment)
