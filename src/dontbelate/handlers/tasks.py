import datetime
import urllib
import xml.etree.ElementTree as ET
from base64 import b64encode

from google.appengine.api import urlfetch
from google.appengine.api import users

from base import handlers
from dontbelate import settings
from dontbelate.models import Profile


def _basic_auth_str(username, password):
    """Returns a Basic Auth string."""
    return 'Basic ' + b64encode('{}:{}'.format(username, password).encode('latin1')).strip()


def call_ns_api(station_from, station_to, departure_time):
    ns_api_base_url = 'http://webservices.ns.nl/ns-api-treinplanner'
    basic_auth = settings.NS_API_BASIC_AUTH
    num_previous_advices = 0
    include_high_speed = 'true'
    now = datetime.datetime.now()
    departure_time = now.replace(hour=departure_time.hour, minute=departure_time.minute).strftime('%Y-%m-%dT%H:%M')
    params = {
        'fromStation': station_from,
        'toStation': station_to,
        'hslAllowed': include_high_speed,
        'previousAdvices': num_previous_advices,
        'dateTime': departure_time,
    }
    url = '{}?{}'.format(ns_api_base_url, urllib.urlencode(params))
    response = urlfetch.fetch(
        url=url,
        headers={'Authorization': _basic_auth_str(*basic_auth)}
    )
    if response.status_code != 200:
        raise
    return parse_ns_api_result(response.content)


def parse_ns_api_result(xml):
    tree = ET.fromstring(xml)
    delays = []
    for element in tree.iter('ReisMogelijkheid'):
        print element.find('Status').text
        departure_planned = element.find('GeplandeVertrekTijd').text
        departure_planned = datetime.datetime.strptime(departure_planned[:-5], settings.NS_DATE_TIME_FORMAT)
        departure_actual = element.find('ActueleVertrekTijd').text
        departure_actual = datetime.datetime.strptime(departure_actual[:-5], settings.NS_DATE_TIME_FORMAT)
        delay = departure_actual - departure_planned
        #import pdb; pdb.set_trace()
        if not delay.seconds:
            continue
        delay = delay.seconds / 60
        train_type = element.find('ReisDeel').find('VervoerType').text
        track_elem = element.find('ReisDeel').find('ReisStop').find('Spoor')
        track = track_elem.text
        track_change = False if track_elem.attrib.get('wijziging') == 'false' else True
        delays.append({
            'train_type': train_type,
            'track_change': track_change,
            'track': track,
            'departure_planned': departure_planned.strftime('%H:%M'),
            'departure_actual': departure_actual.strftime('%H:%M'),
            'delay': delay,
        })
    return delays


def check_routes(routes):
    delays = []
    for route in routes:
        if not route.profile.boxcar_send_push:
            continue
        delays.extend(call_ns_api(route.station_from, route.station_to, route.departure_time_from))
    return delays


class FetchAPI(handlers.AdminHandler):

    def get(self):
        profiles = Profile.query().fetch(limit=500)
        routes_to_check = []
        for profile in profiles:
            routes = profile.get_routes()
            for route in routes:
                if not route.key:
                    continue
                now = datetime.datetime.now()
                if route.departure_time_from_offset <= now.time() <= route.departure_time_until:
                    route.profile = profile
                    routes_to_check.append(route)
        import pdb; pdb.set_trace()
        delays = check_routes(routes_to_check)

        #delays = fetch_ns_api()
        self.render('admin/ns_api_results.tpl', {
            'delays': delays,
        })


    def DenyAccess(self):
        self.redirect(users.create_login_url(self.request.path))

    def XsrfFail(self):
        self.render('error.tpl', {'message': 'XSRF token error'})


class PollAPI(handlers.BaseCronHandler):

    def get(self):
        call_ns_api()


