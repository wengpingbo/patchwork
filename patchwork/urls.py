# Patchwork - automated patch tracking system
# Copyright (C) 2008 Jeremy Kerr <jk@ozlabs.org>
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

from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views

from patchwork import views
from patchwork.views import api as api_views
from patchwork.views import bundle as bundle_views
from patchwork.views import cover as cover_views
from patchwork.views import help as help_views
from patchwork.views import mail as mail_views
from patchwork.views import patch as patch_views
from patchwork.views import discuss as discuss_views
from patchwork.views import project as project_views
from patchwork.views import pwclient as pwclient_views
from patchwork.views import user as user_views
from patchwork.views import xmlrpc as xmlrpc_views


admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', project_views.list, name='project-list'),
    url(r'^project/(?P<project_id>[^/]+)/list/$', patch_views.list,
        name='patch-list'),
    url(r'^project/(?P<project_id>[^/]+)/bundles/$', bundle_views.bundles,
        name='bundle-list'),
    url(r'^project/(?P<project_id>[^/]+)/$', project_views.project,
        name='project-detail'),

    # patch views
    url(r'^patch/(?P<patch_id>\d+)/$', patch_views.patch,
        name='patch-detail'),
    url(r'^patch/(?P<patch_id>\d+)/raw/$', patch_views.content,
        name='patch-raw'),
    url(r'^patch/(?P<patch_id>\d+)/mbox/$', patch_views.mbox,
        name='patch-mbox'),

    # cover views
    url(r'^cover/(?P<cover_id>\d+)/$', cover_views.cover,
        name='cover-detail'),

    url(r'^project/(?P<project_id>[^/]+)/discuss/$', discuss_views.list,
        name='discuss-list'),
    url(r'^discuss/(?P<discuss_id>\d+)/$', discuss_views.discuss,
        name='discuss-detail'),

    # logged-in user stuff
    url(r'^user/$', user_views.profile, name='user-profile'),
    url(r'^user/todo/$', user_views.todo_lists,
        name='user-todos'),
    url(r'^user/todo/(?P<project_id>[^/]+)/$', user_views.todo_list,
        name='user-todo'),
    url(r'^user/bundles/$', bundle_views.bundles,
        name='user-bundles'),

    url(r'^user/link/$', user_views.link,
        name='user-link'),
    url(r'^user/unlink/(?P<person_id>[^/]+)/$', user_views.unlink,
        name='user-unlink'),

    # password change
    url(r'^user/password-change/$', auth_views.password_change,
        name='password_change'),
    url(r'^user/password-change/done/$', auth_views.password_change_done,
        name='password_change_done'),
    url(r'^user/password-reset/$', auth_views.password_reset,
        name='password_reset'),
    url(r'^user/password-reset/mail-sent/$', auth_views.password_reset_done,
        name='password_reset_done'),
    url(r'^user/password-reset/(?P<uidb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm,
        name='password_reset_confirm'),
    url(r'^user/password-reset/complete/$',
        auth_views.password_reset_complete,
        name='password_reset_complete'),

    # login/logout
    url(r'^user/login/$', auth_views.login,
        {'template_name': 'patchwork/login.html'},
        name='auth_login'),
    url(r'^user/logout/$', auth_views.logout,
        {'next_page': '/'},
        name='auth_logout'),

    # registration
    url(r'^register/', user_views.register, name='user-register'),

    # public view for bundles
    url(r'^bundle/(?P<username>[^/]*)/(?P<bundlename>[^/]*)/$',
        bundle_views.bundle,
        name='bundle-detail'),
    url(r'^bundle/(?P<username>[^/]*)/(?P<bundlename>[^/]*)/mbox/$',
        bundle_views.mbox,
        name='bundle-mbox'),

    url(r'^confirm/(?P<key>[0-9a-f]+)/$', views.confirm,
        name='confirm'),

    # submitter autocomplete
    url(r'^submitter/$', api_views.submitters, name='api-submitters'),
    url(r'^delegate/$', api_views.delegates, name='api-delegates'),

    # email setup
    url(r'^mail/$', mail_views.settings, name='mail-settings'),
    url(r'^mail/optout/$', mail_views.optout, name='mail-optout'),
    url(r'^mail/optin/$', mail_views.optin, name='mail-optin'),

    # help!
    url(r'^help/(?P<path>.*)$', help_views.help, name='help'),
]

if 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

if settings.ENABLE_XMLRPC:
    urlpatterns += [
        url(r'xmlrpc/$', xmlrpc_views.xmlrpc, name='xmlrpc'),
        url(r'^pwclient/$', pwclient_views.pwclient,
            name='pwclient'),
        url(r'^project/(?P<project_id>[^/]+)/pwclientrc/$',
            pwclient_views.pwclientrc,
            name='pwclientrc'),
    ]

if settings.ENABLE_REST_API:
    if 'rest_framework' not in settings.INSTALLED_APPS:
        raise RuntimeError(
            'djangorestframework must be installed to enable the REST API.')
    from patchwork.views.rest_api import router, patches_router
    urlpatterns += [
        url(r'^api/1.0/', include(router.urls, namespace='api_1.0')),
        url(r'^api/1.0/', include(patches_router.urls, namespace='api_1.0')),
    ]

# redirect from old urls
if settings.COMPAT_REDIR:
    urlpatterns += [
        url(r'^user/bundle/(?P<bundle_id>[^/]+)/$',
            bundle_views.bundle_redir,
            name='bundle-redir'),
        url(r'^user/bundle/(?P<bundle_id>[^/]+)/mbox/$',
            bundle_views.mbox_redir,
            name='bundle-mbox-redir'),
    ]
