from google.appengine.api import users

from base import handlers
from dontbelate.api import check_routes
from dontbelate.api import find_routes_to_check


class FetchAPI(handlers.AdminHandler):

    def get(self):
        routes_to_check = find_routes_to_check()
        delays = check_routes(routes_to_check)
        self.render('admin/ns_api_results.tpl', {
            'delays': delays,
        })


    def DenyAccess(self):
        self.redirect(users.create_login_url(self.request.path))

    def XsrfFail(self):
        self.render('error.tpl', {'message': 'XSRF token error'})


class PollAPI(handlers.BaseCronHandler):

    def get(self):
        routes_to_check = find_routes_to_check()
        check_routes(routes_to_check)
