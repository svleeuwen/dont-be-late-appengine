from google.appengine.ext import ndb

from base import handlers
from tango import settings


def serializable(model_instance, serializer, language_code):
    # check handler serializer first
    if serializer is not None:
        obj = serializer.serializable(model_instance, language_code)
    else:
        # try fall back to model `serializable` method
        try:
            obj = model_instance.serializable(language_code)
        except ValueError:
            # use `to_dict()` as a last resort
            obj = model_instance.to_dict()
    return obj


class AjaxListHandler(handlers.BaseAjaxHandler):
    """
    Base list handler.

    Usage:
        Add the following class attrs to your handler.
        model: model class
        serializer: serializer to use. defaults to model_instance.serializable
    """
    def get(self):
        language_code = self.request.get('lang', None)
        self.render_json({
            'status': 'ok',
            'status_code': 200,
            'data': self.get_object_list(language_code=language_code),
        })

    def render_error(self, message):
        self.render_json({
            'status': 'error',
            'status_code': 400,
            'error': message,
        })

    def get_query(self):
        return self.model.query()

    def get_object_list(self, **kwargs):
        model = getattr(self, 'model', None)
        if model is None:
            raise NotImplementedError('Handler should have an attribute `model`')

        language_code = kwargs.get('language_code')
        order = kwargs.get('order', '')
        # todo: implement filters
        filters = kwargs.get('filters', [])

        query = self.get_query()
        if filters:
            query = query.filter(*filters)
        if order:
            query = query.order(order)

        object_list = []
        serializer = getattr(self, 'serializer', None)
        for model_instance in query:
            obj = serializable(model_instance, serializer, language_code)
            object_list.append(obj)
        return object_list


class AjaxDetailHandler(handlers.BaseAjaxHandler):
    """
    Base object detail handler.

    Usage:
        Add the following class attrs to your handler.
        model: model class
        serializer: serializer to use. defaults to model_instance.serializable
    """

    def get(self, obj_id):
        languages_available = [lang for lang, label in settings.LANGUAGES]
        language_code = self.request.get('lang', settings.DEFAULT_LANGUAGE)
        if language_code and language_code not in languages_available:
            return self.render_error('Language \'{}\' is not a valid language. '
                                     'Choose one of {}'.format(language_code,
                                                       ', '.join(languages_available)))
        try:
            obj = self.get_object(
                id=obj_id,
                language_code=language_code,
            )
        except ValueError:
            return self.render_error('Invalid id \'{}\''.format(obj_id), 400)

        if not obj:
            return self.render_error(
                '{} with id  \'{}\' not found'.format(self.model.__name__, obj_id),
                status_code=404,
            )
        self.render_json({
            'status': 'ok',
            'status_code': 200,
            'data': obj,
        })

    def render_error(self, message, status_code=400):
        self.render_json({
            'status': 'error',
            'status_code': status_code,
            'error': message,
        })

    def get_object(self, **kwargs):
        model = getattr(self, 'model', None)
        assert model, 'Handler should have an attribute `model`'
        try:
            model_instance = model.get_by_id(int(kwargs.get('id')))
        except ValueError:
            raise
        if not model_instance:
            return
        language_code = kwargs.get('language_code')
        serializer = getattr(self, 'serializer', None)
        assert serializer, 'Handler should have an attribute `serializer`'
        return serializable(model_instance, serializer, language_code)
