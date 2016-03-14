from google.appengine.api import urlfetch
from google.appengine.ext import ndb

from base import handlers
from base.handlers import AdminAjaxHandler
from generic import utils
from generic.utils import valid_slug
from dontbelate import settings


class AdminBaseDetailHandler(handlers.AdminHandler):
    """
    Base object detail handler.

    Usage:
        Add the following class attrs to your handler.
        model: model class
        id_url_kwarg: url kwarg used in route
        template_name: template name
    """
    slug_fields = [('slug_en', 'Slug EN'), ('slug_pt', 'Slug PT')]
    template_name = None
    id_url_kwarg = 'obj_id'

    def get_object(self, *args, **kwargs):
        object_id = kwargs.get(self.id_url_kwarg)
        try:
            object_id = int(object_id)
        except ValueError:
            return self.abort(404)

        obj = self.model.get_by_id(object_id)
        if not obj:
            return self.abort(404)
        return obj

    def get(self, *args, **kwargs):
        self.render(self.template_name,
                    self.get_context_data(object=self.get_object(*args, **kwargs)))

    def get_context_data(self, **kwargs):
        return kwargs

    def render_with_errors(self, obj, errors):
        self.render(self.template_name,
                    self.get_context_data(object=obj, errors=errors))

    def save_slugs(self, obj, errors):
        """
        Call this method when saving form data

        When calling this, it assumes the properties in self.slug_fields
        are available on self.model
        """
        for slug_name, label in self.slug_fields:
            slug_value = self.request.get(slug_name)
            slug_value = slug_value.strip()
            setattr(obj, slug_name, slug_value)
            if not slug_value:
                errors.append('{} is required'.format(label))
                return
            if len(slug_value) < settings.MIN_SLUG_LENGTH:
                errors.append('{} needs to be at least {} characters long.'.format(label, settings.MIN_SLUG_LENGTH))
            if not valid_slug(slug_value):
                errors.append('Enter a valid {} consisting of letters, numbers, underscores or hyphens.'.format(label))
            else:
                # check if obj with provided slug already exists
                query = self.model.query(getattr(self.model, slug_name) == slug_value)
                query = [item for item in query if not item == obj]
                if query:
                    errors.append('{} with {} \'{}\' already exists'.format(self.model.__name__, label, slug_value))


class AdminImageUploadHandler(AdminAjaxHandler):
    """
    Handles image upload from Croppic
    """

    def post(self):
        image_file = self.request.get('img')
        thumbnail = utils.handle_image_upload(image_file)
        self.render_json({
            'status': 'success',
            'url': thumbnail.url,
            'width': thumbnail.width,
            'height': thumbnail.height,
        })

    def DenyAccess(self):
        self.render_json({'status': 'error', 'message': 'No access granted'})

    def XsrfFail(self):
        self.render_json({'status': 'error', 'message': 'XSRF token error'})


class AdminImageCropHandler(AdminAjaxHandler):
    """
    Handles image crop from Croppic
    """

    def post(self):
        # handle image upload here
        image_url = self.request.get('imgUrl')
        image_w = int(float(self.request.get('imgW')))
        image_h = int(float(self.request.get('imgH')))
        image_x1 = float(self.request.get('imgX1'))
        image_y1 = float(self.request.get('imgY1'))
        crop_width = float(self.request.get('cropW'))
        crop_height = float(self.request.get('cropH'))

        image_file = urlfetch.fetch(image_url).content
        thumbnail = utils.handle_image_crop(image_file, image_w, image_h, image_x1, image_y1, crop_width, crop_height)
        self.render_json({
            'status': 'success',
            'url': thumbnail.url,
        })

    def DenyAccess(self):
        self.render_json({'status': 'error', 'message': 'No access granted'})

    def XsrfFail(self):
        self.render_json({'status': 'error', 'message': 'XSRF token error'})


class AdminActionMixin(object):
    """
    Adds action handling to admin change list handler.

    Currently handles delete, publish and unpublish action.
    Could hold more in the future.

    Usage:
        - Add a class attribute `model` to your handler
          which should be set to the model class
        - If `post` is implemented in the AdminHandler,
          call `self.handle_action` in it. See implementation in `post` below.
        - Make sure the change list html is wrapped in a <form>
    """
    DELETE = 'delete'
    PUBLISH = 'publish'
    UNPUBLISH = 'unpublish'
    actions = [
        (DELETE, 'Delete selected items'),
    ]

    def get_actions(self):
        return self.render_to_string('admin/includes/actions.tpl', {
            'actions': self.actions,
        })

    def handle_action(self, **kwargs):
        action = self.request.get('_action')
        if action not in [item[0] for item in self.actions]:
            return

        ids = self.request.get_all('_selected_action')
        if not ids:
            self.add_message('No items selected')
            return
        keys = [ndb.Key(urlsafe=_id) for _id in ids]

        # update with extra keys
        extra_keys = kwargs.get('extra_keys', [])
        keys.extend(extra_keys)

        if action in [self.PUBLISH, self.UNPUBLISH]:
            objects = ndb.get_multi(keys)
            for obj in objects:
                obj.published = action == self.PUBLISH
            ndb.put_multi(objects)
            count = len(objects)
            self.add_message('Successfully {}ed {} items'.format(action, count))
            # after delete redirect to current path (prevents replaying the post)
            return self.redirect(self.request.path)

        # we're dealing with delete
        # check if user confirmed, otherwise show confirmation page
        if self.request.get('_confirm'):
            # already confirmed, delete objects
            deleted = ndb.delete_multi(keys)
            self.add_message('Deleted {} items'.format(len(deleted)))
            return self.redirect(self.request.path)

        # show confirmation page
        context = {
            'object_list': ndb.get_multi(keys),
            'cancel_url': self.request.path,
        }
        self.render('admin/confirm_delete.tpl', context)
        return True

    def post(self, **kwargs):
        if not self.handle_action(**kwargs):
            self.get(**kwargs)