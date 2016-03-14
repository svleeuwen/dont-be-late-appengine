# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
"""Main application entry point."""

import webapp2
from webapp2_extras.routes import RedirectRoute

import base
import base.constants
import handlers
import android_apps.handlers.admin
import android_apps.handlers.api
import dontbelate.handlers.tasks
import dontbelate.handlers.admin

# These should all inherit from base.handlers.BaseHandler
_UNAUTHENTICATED_ROUTES = [
    ('/', handlers.RootHandler),
]

# These should all inherit from base.handlers.BaseAjaxHandler
_UNAUTHENTICATED_AJAX_ROUTES = [
    ('/csp', handlers.CspHandler),
    webapp2.Route('/api/app/<language_code:[-\w]+>/proto', android_apps.handlers.api.AppListProtoBufHandler),
]

# These should all inherit from base.handlers.AuthenticatedHandler
_USER_ROUTES = []

# These should all inherit from base.handlers.AuthenticatedAjaxHandler
_AJAX_ROUTES = []

# These should all inherit from base.handlers.AdminHandler
_ADMIN_ROUTES = [
    RedirectRoute('/admin', dontbelate.handlers.admin.AdminRootHandler, strict_slash=True, name='admin:root'),
    webapp2.Route('/admin/dont-be-late', dontbelate.handlers.tasks.FetchAPI, name='admin:fetch_ns_api'),
    webapp2.Route('/admin/profile', dontbelate.handlers.admin.AdminProfileListHandler, name='admin:profile_list'),
    webapp2.Route('/admin/profile/add', dontbelate.handlers.admin.AdminProfileAddHandler, name='admin:profile_add'),
    webapp2.Route('/admin/profile/<obj_id:\d+>', dontbelate.handlers.admin.AdminProfileEditHandler, name='admin:profile_edit'),
    webapp2.Route('/admin/profile/<obj_id:\d+>/delete', dontbelate.handlers.admin.AdminProfileDeleteHandler, name='admin:profile_delete'),
]


# These should all inherit from base.handlers.AdminAjaxHandler
_ADMIN_AJAX_ROUTES = []

# These should all inherit from base.handlers.BaseCronHandler
_CRON_ROUTES = []

# These should all inherit from base.handlers.BaseTaskHandler
_TASK_ROUTES = [
    webapp2.Route('/poll-api', dontbelate.handlers.tasks.PollAPI, name='poll_api'),
]

# Place global application configuration settings (e.g. settings for
# 'webapp2_extras.sessions') here.
#
# These values will be accessible from handler methods like this:
# self.app.config.get('foo')
#
# Framework level settings:
#   template: one of base.constants.JINJA2 (default) or base.constants.DJANGO.
#
#   using_angular: True or False (default).  When True, an XSRF-TOKEN cookie
#                  will be set for interception/use by Angular's $http service.
#                  When False, no header will be set (but an XSRF token will
#                  still be available under the _xsrf key for Django/Jinja
#                  templates).  If you set this to True, be especially careful
#                  when mixing Angular and Django/Jinja2 templates:
#                    https://github.com/angular/angular.js/issues/5601
#                  See the summary by IgorMinar for details.
#
#   framing_policy: one of base.constants.DENY (default),
#                   base.constants.SAMEORIGIN, or base.constants.PERMIT
#
#   hsts_policy:    A dictionary with minimally a 'max_age' key, and optionally
#                   a 'includeSubdomains' boolean member.
#                   Default: { 'max_age': 2592000, 'includeSubDomains': True }
#                   implying 30 days of strict HTTPS for all subdomains.
#
#   csp_policy:     A dictionary with keys that correspond to valid CSP
#                   directives, as defined in the W3C CSP 1.1 spec.  Each
#                   key/value pair is transmitted as a distinct
#                   Content-Security-Policy header.
#                   Default: {'default-src': '\'self\''}
#                   which is a very restrictive policy.  An optional
#                   'reportOnly' boolean key substitutes a
#                   'Content-Security-Policy-Report-Only' header
#                   name in lieu of 'Content-Security-Policy' (the default
#                   is base.constants.DEBUG).
#
#  Note that the default values are also configured in app.yaml for files
#  served via the /static/ resources.  You may need to change the settings
#  there as well.

_CONFIG = {
    # Developers are encouraged to build sites that comply with this (or
    # a similarly restrictive) CSP policy.  In particular, adding directives
    # such as unsafe-inline or unsafe-eval is highly discouraged, as these
    # may lead to XSS attacks.
    'csp_policy': {
        # Fallback.
        'default-src': '\'self\'',
        # Disallow Flash, etc.
        'object-src': '\'none\'',
        # Images stored in Google Cloud Storage.
        'img-src': '\'self\' https://*.googleusercontent.com',
        # hashes for inline admin scripts
        'script-src': '\'self\' '
                      '\'sha256-UJTyccto2VcmDTExLsNUE+yXftTqSxxFel9MqQsA2UI=\' '
                      '\'sha256-wGT5D3ZixUjzWFZmdnI7IbZ50msIkD6EtjmvuYfC5L0=\' '
                      '\'sha256-9pt6fFhBGDnOj9zFk4XYSRW3iRKzic7urgQBXM5vGrE=\' '
                      '\'sha256-Nn8qbLFAjUUBiNU9McCyH/sZmAMI1k00h37ZCK4Mc/Y=\' ',
        # Maps, YouTube provide <iframe> based embedding at these URIs.
        'child-src':  '\'self\' https://www.google.com https://www.youtube.com',
        # Deprecated. Used for supporting browsers that use CSP 1.0 only.
        'frame-src':  '\'self\' https://www.google.com https://www.youtube.com',
        # In generated code from http://www.google.com/fonts
        'style-src':  '\'self\' https://fonts.googleapis.com '
                      'https://*.gstatic.com',
        # https://developers.google.com/fonts/docs/technical_considerations
        'font-src':   '\'self\' https://themes.googleusercontent.com '
                      'https://*.gstatic.com',
        'report-uri': '/csp',
        'reportOnly': base.constants.DEBUG,
    },
    'webapp2_extras.sessions': {
        'secret_key': '3a9b8277b7914e65bfad1bd317b7693c',
    },
}

#################################
# DO NOT MODIFY BELOW THIS LINE #
#################################

app = webapp2.WSGIApplication(
    routes=(_UNAUTHENTICATED_ROUTES + _UNAUTHENTICATED_AJAX_ROUTES +
            _USER_ROUTES + _AJAX_ROUTES + _ADMIN_ROUTES + _ADMIN_AJAX_ROUTES +
            _CRON_ROUTES + _TASK_ROUTES),
    debug=base.constants.DEBUG,
    config=_CONFIG)
