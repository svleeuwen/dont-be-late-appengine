from google.appengine.ext import ndb


class Profile(ndb.Model):
    user_id = ndb.StringProperty()
    boxcar_access_token = ndb.StringProperty(indexed=False)
    boxcar_send_push = ndb.BooleanProperty(default=True)
    routes = ndb.KeyProperty(repeated=True)
    silence_until = ndb.DateTimeProperty()

    def __unicode__(self):
        return u'Profile {}'.format(self.user_id)

    def get_routes(self):
        routes = ndb.get_multi(self.routes)
        routes.append(Route())
        return routes


class Route(ndb.Model):
    station_from = ndb.StringProperty()
    station_to = ndb.StringProperty()
    departure_time_from = ndb.TimeProperty()
    departure_time_until = ndb.TimeProperty()
    # when to start polling
    departure_time_from_offset = ndb.TimeProperty()
    # hash of latest push message
    latest_push_message = ndb.StringProperty(indexed=False)
    weekdays_only = ndb.BooleanProperty(default=True)
