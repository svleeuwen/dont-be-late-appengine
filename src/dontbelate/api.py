import datetime
import urllib
import xml.etree.ElementTree as ET
from base64 import b64encode

from google.appengine.api import urlfetch

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
    return parse_ns_api_result(response.content, station_from, station_to)


def parse_ns_api_result(xml, station_from, station_to):
    tree = ET.fromstring(xml)
    delays = []
    for element in tree.iter('ReisMogelijkheid'):
        print element.find('Status').text
        departure_planned = element.find('GeplandeVertrekTijd').text
        departure_planned = datetime.datetime.strptime(departure_planned[:-5], settings.NS_DATE_TIME_FORMAT)
        departure_actual = element.find('ActueleVertrekTijd').text
        departure_actual = datetime.datetime.strptime(departure_actual[:-5], settings.NS_DATE_TIME_FORMAT)
        delay = departure_actual - departure_planned
        if not delay.seconds:
            continue
        delay = delay.seconds / 60
        train_type = element.find('ReisDeel').find('VervoerType').text
        track_elem = element.find('ReisDeel').find('ReisStop').find('Spoor')
        track = track_elem.text
        track_change = False if track_elem.attrib.get('wijziging') == 'false' else True
        delays.append({
            'station_from': station_from,
            'station_to': station_to,
            'train_type': train_type,
            'track_change': track_change,
            'track': track,
            'departure_planned': departure_planned.strftime('%H:%M'),
            'departure_actual': departure_actual.strftime('%H:%M'),
            'delay': delay,
        })
    return delays


def create_push_message(delays):
    out = ''
    out_long = ''
    for i, delay in enumerate(delays):
        out += '{departure_planned}: (+{delay}) sp. {track}'.format(**delay)
        # add exclamation emoji if track changed
        if delay['track_change']:
            out += '\xE2\x9D\x97'
        out_long += '{station_from} - {station_to} {departure_planned}: (+{delay}) sp. {track} ({train_type})'.format(**delay)
        if i < len(delays) - 1:
            out += ', '
            out_long += '\n'
        else:
            out += '.'
    return out, out_long


def send_push_notification(message, message_long, access_token):
    boxcar_api_base_url = 'https://new.boxcar.io/api/notifications'
    params = {
        'user_credentials': access_token,
        'notification[title]': message,
        'notification[long_message]': message_long,
    }
    response = urlfetch.fetch(
        url=boxcar_api_base_url,
        payload=urllib.urlencode(params),
        method=urlfetch.POST
    )
    if response.status_code != 201:
        print response.content


def check_routes(routes):
    all_delays = []
    for route in routes:
        if not route.profile.boxcar_send_push:
            continue
        delays = call_ns_api(route.station_from, route.station_to, route.departure_time_from)
        if not delays:
            continue
        boxcar_access_token = route.profile.boxcar_access_token
        message, message_long = create_push_message(delays)
        hashed_message = hash(message)
        if route.latest_push_message != hashed_message:
            route.latest_push_message = hashed_message
            route.put()
            send_push_notification(message, message_long, boxcar_access_token)
        all_delays.extend(delays)
    return all_delays


def find_routes_to_check():
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
    return routes_to_check
