# coding=utf-8
import datetime

from google.appengine.api import datastore_types
from google.appengine.ext import ndb

from generic import utils
from tango import settings


class BaseModelSerializer(object):
    exclude = []
    fields = []
    language_fields = []

    @classmethod
    def serializable(cls, model_instance, language_code=None):
        """
        Convert model_instance to a json serializable object

        Args:
            model_instance: ndb.Model instance
            language_code: One of language_codes in settings.LANGUAGES

        Returns:
            dictionary that can be safely serialized using json.dumps
        """
        obj = model_instance.to_dict()

        # handle includes and excludes
        exclude = []
        if cls.fields:
            exclude = [key for key in obj.keys() if key not in cls.fields]
        elif cls.exclude:
            exclude = cls.exclude
        for field in exclude:
            if field in obj:
                del obj[field]

        # serialize some value types right away
        for key, value in obj.items():
            if isinstance(value, datetime.datetime):
                obj[key] = value.strftime('%Y-%m-%d %H:%M')
            if isinstance(value, datastore_types.GeoPt):
                obj[key] = {'lat': value.lat, 'lng': value.lon}
            if isinstance(value, ndb.Key):
                obj[key] = value.urlsafe()

            # if language_code is available make sure
            # only that language is available in the obj
            languages_available = [lang for lang, label in settings.LANGUAGES]
            if language_code in languages_available and key in cls.language_fields:
                del obj[key]
                if key.endswith(language_code):
                    key = key.rsplit('_', 1)[0]
                    obj[key] = value

        # add generic fields
        obj['_type'] = getattr(model_instance, '_type', None) or model_instance.__class__.__name__.lower()
        if model_instance.key:
            obj['_id'] = model_instance.key.id()

        # optional metadata contains a lot of crap characters, remove it
        if '__metadata__' in obj:
            del obj['__metadata__']

        # add extra data
        obj.update(cls.get_extra_data(model_instance, language_code))
        return obj

    @classmethod
    def get_extra_data(cls, model_instance, language_code=None):
        return {}
