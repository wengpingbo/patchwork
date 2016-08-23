# Patchwork - automated patch tracking system
# Copyright (C) 2016 Intel Corporation
#
# This file is part of the Patchwork package.
#
# Patchwork is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Patchwork is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Patchwork; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from __future__ import absolute_import

from django.core import urlresolvers
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response, get_object_or_404

from patchwork.views import submission_list
from patchwork.models import DiscussThread, Submission, Project
from patchwork.paginator import Paginator


def discuss(request, discuss_id):
    context = {}

    try:
        discuss = get_object_or_404(DiscussThread, id=discuss_id)
    except Http404 as exc:
        raise exc

    context = {
        'submission': discuss,
        'project': discuss.project,
    }

    return render_to_response('patchwork/submission.html', context)

def list(request, project_id):
    project = get_object_or_404(Project, linkname=project_id)
    discuss = DiscussThread.objects.filter(project=project)

    context = submission_list(request, project, 'discuss-list',
                           view_args={'project_id': project.linkname},
                           subms=discuss)
    return render(request, 'patchwork/discuss-list.html', context)
