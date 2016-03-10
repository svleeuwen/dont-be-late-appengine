import datetime

from google.appengine.api import users
from webapp2 import uri_for

from base import handlers
from dontbelate.models import Profile, Route
from generic.handlers.admin.admin import AdminBaseDetailHandler


class AdminRootHandler(handlers.AdminHandler):
    def get(self):
        self.render('admin/home.tpl', {})

    def DenyAccess(self):
        self.redirect(users.create_login_url(self.request.path))

    def XsrfFail(self):
        self.render('error.tpl', {'message': 'XSRF token error'})


class AdminProfileListHandler(handlers.AdminHandler):
    model = Profile

    def get(self):
        context = {
            'object_list': self.model.query().fetch(limit=500),
            'messages': self.messages,
        }
        self.render('admin/profile_list.tpl', context)

    def DenyAccess(self):
        self.redirect(users.create_login_url(self.request.path))

    def XsrfFail(self):
        self.render('error.tpl', {'message': 'XSRF token error'})


class AdminProfileEditHandler(AdminBaseDetailHandler):
    model = Profile
    id_url_kwarg = 'obj_id'
    template_name = 'admin/profile_add_edit.tpl'

    def get_context_data(self, *args, **kwargs):
        context = {
            'messages': self.messages,
        }
        context.update(kwargs)
        return context

    def post(self, *args, **kwargs):
        obj = self.get_object(*args, **kwargs)
        obj, errors = self.save_form_data(obj)

        if not errors:
            obj.put()
            self.add_message('Item saved')
            self.get(*args, **kwargs)
        else:
            self.render_with_errors(obj, errors)

    def save_form_data(self, obj):
        errors = []

        obj.user_id = users.get_current_user().user_id()

        try:
            obj.boxcar_send_push = self.request.get('boxcar_send_push') == 'on'
        except ValueError:
            pass

        obj.boxcar_access_token = self.request.get('boxcar_access_token')

        obj.routes = []
        station_from_list = self.request.get_all('station_from')
        station_to_list = self.request.get_all('station_to')
        departure_time_from_list = self.request.get_all('departure_time_from')
        departure_time_until_list = self.request.get_all('departure_time_until')
        departure_time_from_offset_list = self.request.get_all('departure_time_from_offset')
        route_id_list = self.request.get_all('route_id')
        delete_list = self.request.get_all('delete')

        routes = zip(
            route_id_list,
            station_from_list,
            station_to_list,
            departure_time_from_list,
            departure_time_until_list,
            departure_time_from_offset_list
        )

        for route_id, station_from, station_to, departure_time_from, departure_time_until, departure_time_from_offset in routes:
            if not all([station_from, station_to, departure_time_from, departure_time_until]):
                continue
            if not route_id:
                route = Route()
            else:
                route = Route.get_by_id(int(route_id))
                if route_id in delete_list:
                    route.key.delete()
                    continue
            route.station_from = station_from
            route.station_to = station_to
            route.departure_time_from = datetime.datetime.strptime(departure_time_from, '%H:%M').time()
            route.departure_time_until = datetime.datetime.strptime(departure_time_until, '%H:%M').time()
            if departure_time_from_offset:
                route.departure_time_from_offset = datetime.datetime.strptime(departure_time_from_offset, '%H:%M').time()
            route.put()
            obj.routes.append(route.key)
        return obj, errors

    def DenyAccess(self):
        self.redirect(users.create_login_url(self.request.path))

    def XsrfFail(self):
        self.render('error.tpl', {'message': 'XSRF token error'})


class AdminProfileAddHandler(AdminProfileEditHandler):
    def get_object(self, *args, **kwargs):
        return Profile()

    def post(self, *args, **kwargs):
        obj = self.get_object(*args, **kwargs)
        obj, errors = self.save_form_data(obj)

        if not errors:
            obj.put()
            self.add_message('Item saved')
            return self.redirect(uri_for('admin:profile_list'))
        else:
            self.render_with_errors(obj, errors)

    def DenyAccess(self):
        self.redirect(users.create_login_url(self.request.path))

    def XsrfFail(self):
        self.render('error.tpl', {'message': 'XSRF token error'})


class AdminProfileDeleteHandler(AdminProfileEditHandler):
    template_name = 'admin/profile_delete.tpl'
    id_url_kwarg = 'obj_id'

    def post(self, *args, **kwargs):
        obj = self.get_object(*args, **kwargs)
        if obj:
            obj.key.delete()
            self.add_message('Item deleted')
            self.redirect(uri_for('admin:profile_list'))
        else:
            self.abort(404)

    def DenyAccess(self):
        self.redirect(users.create_login_url(self.request.path))

    def XsrfFail(self):
        self.render('error.tpl', {'message': 'XSRF token error'})
