from google.appengine.api import app_identity

NS_DATE_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
NS_API_BASIC_AUTH = ('emailaddress', 'api-token')

MIN_SLUG_LENGTH = 3


# General
APP_ID_PRODUCTION = 'dont-be-late'
try:
    APP_ID = app_identity.get_application_id()
except AttributeError:
    # happens when running tests
    APP_ID = 'test'
IS_PRODUCTION = APP_ID == APP_ID_PRODUCTION


try:
    from local_settings import *
except ImportError:
    pass