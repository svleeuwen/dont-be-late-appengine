import datetime
import re
import unicodedata

import pytz

from dontbelate import settings

MAX_DEEPLINK_LENGTH = 40


def generate_slug(s_in):
    s = unicode(s_in)
    s = unicodedata.normalize('NFD', s).encode('ascii', 'ignore')
    s = re.sub(r'[^a-zA-Z0-9\ \-_]', '', s.lower())  # strip non alphanumeric
    s = re.sub(r'[-\s]+', '-', s)  # convert spaces to hyphens
                                   # and remove repeating hyphens
    s = s[:MAX_DEEPLINK_LENGTH]
    if s.isdigit():
        s = "s_%s" % s
    return s


def valid_slug(value):
    match = re.match('^[-a-zA-Z0-9_]+\Z', value)
    return bool(match)


def local_to_utc(date_time):
    """
    Convert local datetime string to UTC
    Remove tzinfo to be able to save to Datastore right away

    Args:
        date_time: str

    Returns:
        naive utc datetime.datetime
    """
    dt = datetime.datetime.strptime(date_time, '%Y-%m-%d %H:%M')
    tz = pytz.timezone(settings.DEFAULT_TIME_ZONE)
    local_dt = tz.localize(dt)
    return local_dt.astimezone(pytz.utc).replace(microsecond=0, tzinfo=None)


def utc_to_local(date_time):
    """
    Convert UTC datetime to local datetime

    Args:
        date_time: utc datetime.datetime

    Returns:
        naive local datetime.datetime
    """
    tz = pytz.timezone(settings.DEFAULT_TIME_ZONE)
    local_dt = date_time.replace(tzinfo=pytz.utc, microsecond=0).astimezone(tz)
    return local_dt.replace(tzinfo=None)