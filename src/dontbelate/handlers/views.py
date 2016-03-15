import datetime

from webapp2 import uri_for

from base import handlers
from dontbelate.models import Profile
from generic.utils import utc_to_local


class ProfileEditHandler(handlers.BaseHandler):

    def get(self, obj_id):
        obj = self.get_object(obj_id)
        if not obj:
            return self.abort(404)

        local_silence_until = None
        if obj.silence_until:
            local_silence_until = utc_to_local(obj.silence_until)
            local_silence_until = local_silence_until.strftime('%H:%M')
        self.render('profile_detail.tpl', {
            'object': obj,
            'silence_until': local_silence_until,
        })

    def post(self, obj_id):
        obj = self.get_object(obj_id)
        if not obj:
            return self.abort(404)

        cancel_silence = self.request.get('cancel_silence')
        if cancel_silence:
            obj.silence_until = None
            obj.put()
            return self.redirect_to_detail(obj_id)

        try:
            silence = int(self.request.get('silence'))
        except ValueError:
            pass
        else:
            now = datetime.datetime.now()
            silence_datetime = now + datetime.timedelta(hours=silence)
            obj.silence_until = silence_datetime
        obj.put()
        self.redirect_to_detail(obj_id)

    def redirect_to_detail(self, obj_id):
        self.redirect(uri_for('profile_edit', obj_id=obj_id))

    def get_object(self, obj_id):
        obj = None
        try:
            obj = Profile.get_by_id(int(obj_id))
        except ValueError:
            pass
        return obj