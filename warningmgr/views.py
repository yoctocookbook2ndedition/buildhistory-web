# buildhistory-web - view definitions
#
# Copyright (C) 2013 Intel Corporation
#
# Licensed under the MIT license, see COPYING.MIT for details

from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.template import RequestContext
from warningmgr.models import WarningItem, Comment
from datetime import datetime
from django.views.generic import DetailView, ListView

def postcomment(request, pk):
    if not request.user.is_authenticated():
        raise PermissionDenied
    w = get_object_or_404(WarningItem, pk=pk)
    comment_text = request.POST['comment_text'].strip()
    if comment_text != '':
        c = w.comment_set.create(comment=request.POST['comment_text'], date=datetime.now(), author=request.user.username)
        c.save()
        return HttpResponseRedirect(reverse('warning_item', args=(w.id,)))
    else:
        return render_to_response('warningmgr/detail.html', {
            'warningitem': w,
            'error_message': "You didn't specify any comment text.",
        }, context_instance=RequestContext(request))

def ignore(request, pk):
    return _statuschange(request, pk, 'I')

def actionreq(request, pk):
    return _statuschange(request, pk, 'A')

def resolve(request, pk):
    return _statuschange(request, pk, 'R')

def unreview(request, pk):
    return _statuschange(request, pk, 'N')

def _statuschange(request, pk, newstatus):
    if not (request.user.is_authenticated() and request.user.has_perm('warningmgr.change_warningitem')):
        raise PermissionDenied
    w = get_object_or_404(WarningItem, pk=pk)
    w.change_status(newstatus, request.user.username)
    w.save()
    return HttpResponseRedirect(reverse('warning_item', args=(w.id,)))


def multi_action(request):
    if not (request.user.is_authenticated() and request.user.has_perm('warningmgr.change_warningitem')):
        raise PermissionDenied
    action = request.POST['action']
    action_statuses = { 'actionreq': 'A', 'resolve': 'R', 'ignore': 'I' }
    if action and action in action_statuses:
        id_list = request.POST.getlist('selecteditems')
        id_list = [int(i) for i in id_list if i.isdigit()]
        warningitems = WarningItem.objects.filter(id__in=id_list)
        for w in warningitems:
            w.change_status(action_statuses[action], request.user.username)
            w.save()

    return HttpResponseRedirect(reverse('warning_list'))


class WarningListView(ListView):
    context_object_name = 'warning_list'
    paginate_by = 20

    def get_queryset(self):
        return WarningItem.objects.filter(status__in=self.request.session.get('status_filter', 'NA')).order_by('created_date')
