import urllib


class AdminFiltersMixin(object):
    """
    Adds filter handling to admin change list handler.

    Currently only handles BooleanProperty properties.

    Usage:
        - Add a class attribute `model` to your handler
          which should be set to the model class
        - Add a class attribute `list_filter` to your handler
          which should be set to a list of property name strings
        - Add the result of `self.get_object_list` to your template context
        - Add the result of `self.get_filters` to your
          template context with key `filters`
    """
    def get_filters(self):
        filters = []
        for prop_name in self.list_filters:
            prop = getattr(self.model, prop_name, None)
            if prop is None:
                continue
            prop_filter = filter_for_property(prop)
            if prop_filter is None:
                continue

            # construct query string for 'All' (or: 'reset this filter')
            query_dict = self.request.GET.copy()
            if prop_name in query_dict:
                del query_dict[prop_name]
            all_query = urllib.urlencode(query_dict.items())

            # create query string for choices
            choices = prop_filter.get_choices()
            for choice in choices:
                query_dict.update({
                    prop_name: choice['value'],
                })
                choice['query'] = urllib.urlencode(query_dict.items())

            filter_html = self.render_to_string(prop_filter.template_name, {
                'title': prop_name.title(),
                'prop_name': prop_name,
                'choices': choices,
                'all_query': all_query,
                'active_choice': self.request.get(prop_name),
            })
            filters.append(filter_html)
        return ''.join(filters)

    def get_query(self):
        filters = self.request.GET
        query = self.model.query()
        query_filters = []
        for key, value in filters.items():
            prop = getattr(self.model, key, None)
            if prop is None:
                continue
            prop_filter = filter_for_property(prop)
            if prop_filter is None:
                continue
            value = prop_filter.parse_value(value)
            query_filters.append(prop_filter.get_filter_arg(value))
        return query.filter(*query_filters)


class BasePropertyFilter(object):
    template_name = 'admin/includes/filter.tpl'

    def __init__(self, prop):
        self.prop = prop

    def get_choices(self):
        """
        Return a list of {'value': x, 'label': y} items
        where value is used in the url query and label is shown
        to the user.
        """
        raise NotImplementedError

    def parse_value(self, value):
        """
        Parse the value to python object
        """
        raise NotImplementedError

    def get_filter_arg(self, value):
        """
        Return a value that can be used as argument for ndb.Query().
        """
        raise NotImplementedError


class BooleanPropertyFilter(BasePropertyFilter):

    def get_choices(self):
        return [
            {'value': '1', 'label': 'Yes'},
            {'value': '0', 'label': 'No'}
        ]

    def parse_value(self, value):
        return True if value == '1' else False

    def get_filter_arg(self, value):
        return self.prop == value


PROPERTY_FILTERS = {
    'BooleanProperty': BooleanPropertyFilter,
}

def filter_for_property(prop):
    name = prop.__class__.__name__
    cls = PROPERTY_FILTERS.get(name)
    if cls:
        return cls(prop)
