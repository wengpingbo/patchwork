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

from __future__ import absolute_import

from django.contrib.auth.models import User
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils import six
from django.utils.six.moves.urllib.parse import quote

from patchwork.models import Person, State


class Filter(object):

    def __init__(self, filters):
        self.filters = filters
        self.applied = False
        self.forced = False

    def name(self):
        """The 'name' of the filter, to be displayed in the filter UI"""
        return self.name

    def condition(self):
        """The current condition of the filter, to be displayed in the
           filter UI"""
        return self.key

    def key(self):
        """The key for this filter, to appear in the querystring. A key of
           None will remove the param=key pair from the querystring."""
        return None

    def set_status(self, *kwargs):
        """Views can call this to force a specific filter status. For example,
           a user's todo page needs to setup the delegate filter to show
           that user's delegated patches"""
        pass

    def parse(self, dict):
        if self.param not in dict:
            return
        self._set_key(dict[self.param])

    def url_without_me(self):
        return self.filters.querystring_without_filter(self)

    def form_function(self):
        return 'function(form) { return "unimplemented" }'

    def form(self):
        if self.forced:
            return mark_safe('<input type="hidden" value="%s">%s' % (
                self.param, self.condition()))
            return self.condition()
        return self._form()

    def kwargs(self):
        return {}

    def __str__(self):
        return '%s: %s' % (self.name, self.kwargs())


class SubmitterFilter(Filter):
    param = 'submitter'

    def __init__(self, filters):
        super(SubmitterFilter, self).__init__(filters)
        self.name = 'Submitter'
        self.person = None
        self.person_match = None

    def _set_key(self, str):
        self.person = None
        self.person_match = None
        submitter_id = None

        str = str.strip()
        if str == '':
            return

        try:
            submitter_id = int(str)
        except ValueError:
            pass
        except:
            return

        if submitter_id:
            self.person = Person.objects.get(id=int(str))
            self.applied = True
            return

        people = Person.objects.filter(name__icontains=str)

        if not people:
            return

        self.person_match = str
        self.applied = True

    def kwargs(self):
        if self.person:
            user = self.person.user
            if user:
                return {'submitter__in':
                        Person.objects.filter(user=user).values('pk').query}
            return {'submitter': self.person}

        if self.person_match:
            return {'submitter__name__icontains': self.person_match}
        return {}

    def condition(self):
        if self.person:
            return self.person.name
        elif self.person_match:
            return self.person_match
        return ''

    def _form(self):
        return mark_safe(('<input type="text" name="submitter" ' +
                          'id="submitter_input" class="form-control">'))

    def key(self):
        if self.person:
            return self.person.id
        return self.person_match


class StateFilter(Filter):
    param = 'state'
    any_key = '*'
    action_req_str = 'Action Required'

    def __init__(self, filters):
        super(StateFilter, self).__init__(filters)
        self.name = 'State'
        self.state = None
        self.applied = True

    def _set_key(self, str):
        self.state = None

        if str == self.any_key:
            self.applied = False
            return

        try:
            self.state = State.objects.get(id=int(str))
        except:
            return

        self.applied = True

    def kwargs(self):
        if self.state is not None:
            return {'state': self.state}
        else:
            return {'state__in':
                    State.objects.filter(action_required=True)
                    .values('pk').query}

    def condition(self):
        if self.state:
            return self.state.name
        return self.action_req_str

    def key(self):
        if self.state is not None:
            return self.state.id
        if not self.applied:
            return '*'
        return None

    def _form(self):
        str = '<select name="%s" class="form-control">' % self.param

        selected = ''
        if not self.applied:
            selected = 'selected'
        str += '<option %s value="%s">any</option>' % (selected, self.any_key)

        selected = ''
        if self.applied and self.state is None:
            selected = 'selected'
        str += '<option %s value="">%s</option>' % (
            selected, self.action_req_str)

        for state in State.objects.all():
            selected = ''
            if self.state and self.state == state:
                selected = ' selected="true"'

            str += '<option value="%d" %s>%s</option>' % (
                state.id, selected, state.name)
        str += '</select>'
        return mark_safe(str)

    def form_function(self):
        return 'function(form) { return form.x.value }'

    def url_without_me(self):
        qs = self.filters.querystring_without_filter(self)
        if qs != '?':
            qs += '&'
        return qs + '%s=%s' % (self.param, self.any_key)


class SubjectFilter(Filter):
    param = 'subject'

    def __init__(self, filters):
        super(SubjectFilter, self).__init__(filters)
        self.name = 'Subject'
        self.param = 'subject'
        self.search = None

    def _set_key(self, str):
        str = str.strip()
        if str == '':
            return
        self.search = str
        self.applied = True

    def kwargs(self):
        return {'name__icontains': self.search}

    def condition(self):
        return self.search

    def key(self):
        return self.search

    def _form(self):
        value = ''
        if self.search:
            value = escape(self.search)
        return mark_safe('<input name="%s" class="form-control" value="%s">' %
                         (self.param, value))

    def form_function(self):
        return mark_safe('function(form) { return form.x.value }')

class ContentFilter(Filter):
    param = 'content'

    def __init__(self, filters):
        super(ContentFilter, self).__init__(filters)
        self.name = 'Patch Path'
        self.param = 'content'
        self.search = None

    def _set_key(self, str):
        str = str.strip()
        if str == '':
            return
        self.search = str
        self.applied = True

    def kwargs(self):
        words = self.search.decode("utf-8").split()

        value = r'\n\s(' + words[0] + r')'
        words.remove(words[0])
        for s in words:
            value += r'|(' + s + r')'
        value += r'.+\.[ch]'

        return {'content__regex': value}

    def condition(self):
        return self.search

    def key(self):
        return self.search

    def _form(self):
        value = ''
        if self.search:
            value = escape(self.search)
        return mark_safe('<input name="%s" class="form-control" value="%s">' %
                         (self.param, value))

    def form_function(self):
        return mark_safe('function(form) { return form.x.value }')

class ArchiveFilter(Filter):
    param = 'archive'

    def __init__(self, filters):
        super(ArchiveFilter, self).__init__(filters)
        self.name = 'Archived'
        self.archive_state = False
        self.applied = True
        self.param_map = {
            True: 'true',
            False: '',
            None: 'both'
        }
        self.description_map = {
            True: 'Yes',
            False: 'No',
            None: 'Both'
        }

    def _set_key(self, str):
        self.archive_state = False
        self.applied = True
        for (k, v) in self.param_map.items():
            if str == v:
                self.archive_state = k
        if self.archive_state is None:
            self.applied = False

    def kwargs(self):
        if self.archive_state is None:
            return {}
        return {'archived': self.archive_state}

    def condition(self):
        return self.description_map[self.archive_state]

    def key(self):
        if not self.archive_state:
            return None
        return self.param_map[self.archive_state]

    def _form(self):
        s = ''
        for b in [False, True, None]:
            label = self.description_map[b]
            selected = ''
            if self.archive_state == b:
                selected = 'checked'
            s += ('<label class="checkbox-inline">'
                  ' <input type="radio" name="%(param)s" '
                  '%(selected)s value="%(value)s">%(label)s'
                  '</label>') % \
                {'label': label,
                 'param': self.param,
                 'selected': selected,
                 'value': self.param_map[b]
                 }
        return mark_safe(s)

    def url_without_me(self):
        qs = self.filters.querystring_without_filter(self)
        if qs != '?':
            qs += '&'
        return qs + 'archive=both'


class DelegateFilter(Filter):
    param = 'delegate'
    AnyDelegate = 1

    def __init__(self, filters):
        super(DelegateFilter, self).__init__(filters)
        self.name = 'Delegate'
        self.delegate = None
        self.delegate_match = None

    def _set_key(self, key):
        self.delegate = None
        self.delegate_match = None
        delegate_id = None

        key = key.strip()
        if not key:
            return

        try:
            delegate_id = int(key)
        except ValueError:
            pass
        except:
            return

        if delegate_id:
            self.delegate = User.objects.get(id=int(key))
            self.applied = True
            return

        delegates = User.objects.filter(username__icontains=key)
        if not delegates:
            return

        self.delegate_match = key
        self.applied = True

    def kwargs(self):
        if self.delegate:
            return {'delegate': self.delegate}

        if self.delegate_match:
            return {'delegate__username__icontains': self.delegate_match}
        return {}

    def condition(self):
        if self.delegate:
            return str(self.delegate)
        elif self.delegate_match:
            return self.delegate_match
        return ''

    def _form(self):
        return mark_safe('<input type="text" name="delegate" '
                         'id="delegate_input" class="form-control">')

    def key(self):
        if self.delegate:
            return self.delegate.id
        return self.delegate_match

    def set_status(self, *args, **kwargs):
        if 'delegate' in kwargs:
            self.applied = self.forced = True
            self.delegate = kwargs['delegate']
        if self.AnyDelegate in args:
            self.applied = False
            self.forced = True


filterclasses = [SubmitterFilter,
                 StateFilter,
                 SubjectFilter,
                 ContentFilter,
                 ArchiveFilter,
                 DelegateFilter]


class Filters:

    def __init__(self, request):
        self._filters = [c(self) for c in filterclasses]
        self.dict = request.GET
        self.project = None

        for f in self._filters:
            f.parse(self.dict)

    def set_project(self, project):
        self.project = project

    def filter_conditions(self):
        kwargs = {}
        for f in self._filters:
            if f.applied:
                kwargs.update(f.kwargs())
        return kwargs

    def apply(self, queryset):
        kwargs = self.filter_conditions()
        if not kwargs:
            return queryset
        return queryset.filter(**kwargs)

    def params(self):
        return [(f.param, f.key()) for f in self._filters
                if f.key() is not None]

    def querystring(self, remove=None):
        params = dict(self.params())

        for (k, v) in self.dict.items():
            if k not in params:
                params[k] = v

        if remove is not None:
            if remove.param in list(params.keys()):
                del params[remove.param]

        def sanitise(s):
            if not isinstance(s, six.string_types):
                s = six.text_type(s)
            return quote(s.encode('utf-8'))

        return '?' + '&'.join(['%s=%s' % (sanitise(k), sanitise(v))
                               for (k, v) in list(params.items())])

    def querystring_without_filter(self, filter):
        return self.querystring(filter)

    def applied_filters(self):
        return [x for x in self._filters if x.applied]

    def available_filters(self):
        return self._filters

    def set_status(self, filterclass, *args, **kwargs):
        for f in self._filters:
            if isinstance(f, filterclass):
                f.set_status(*args, **kwargs)
                return
