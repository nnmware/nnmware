# -*- coding: utf-8 -*-
from datetime import datetime
import os
import Image
import json
from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.middleware import http
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.views.generic.base import View
from django.views.generic.edit import FormMixin
from nnmware.core.http import LazyEncoder
from nnmware.core.models import Pic, Doc
from nnmware.core.backends import PicUploadBackend,DocUploadBackend, AvatarUploadBackend
from nnmware.core.imgutil import resize_image, remove_thumbnails, remove_file

def AjaxAnswer(payload):
    return HttpResponse(json.dumps(payload), content_type='application/json')

def AjaxLazyAnswer(payload):
    return HttpResponse(json.dumps(payload, cls=LazyEncoder), content_type='application/json')

class AjaxAbstractUploader(object):
    def __call__(self, request, **kwargs):
        return self._ajax_upload(request, **kwargs)

    def _upload_file(self, request, **kwargs):
        if request.is_ajax():
            # the file is stored raw in the request
            self.upload = request
            self.is_raw = True
            # AJAX Upload will pass the filename in the querystring if it
            # is the "advanced" ajax upload
            try:
                self.filename = request.GET['qqfile']
            except KeyError:
                return HttpResponseBadRequest("AJAX request not valid")
                # not an ajax upload, so it was the "basic" iframe version with
                # submission via form
        else:
            self.is_raw = False
            if len(request.FILES) == 1:
                # FILES is a dictionary in Django but Ajax Upload gives
                # the uploaded file an ID based on a random number, so it
                # cannot be guessed here in the code. Rather than editing
                # Ajax Upload to pass the ID in the querystring, observe
                # that each upload is a separate request, so FILES should
                # only have one entry. Thus, we can just grab the first
                # (and only) value in the dict.
                self.upload = request.FILES.values()[0]
            else:
                raise Http404("Bad Upload")
            self.filename = self.upload.name
        backend = self.get_backend()

        # custom filename handler
        self.filename = (backend.update_filename(request, self.filename)
                         or self.filename)
        # save the file
        backend.setup(self.filename)
        self.success = backend.upload(self.upload, self.filename, self.is_raw)
        # callback
        self.extra_context = backend.upload_complete(request, self.filename)

    def _new_obj(self, target, request, **kwargs):
        target.content_type = get_object_or_404(ContentType, id=int(kwargs['content_type']))
        target.object_id = int(kwargs['object_id'])
        target.description = self.extra_context['oldname']
        target.user = request.user
        target.publish_date = datetime.now()


class AjaxFileUploader(AjaxAbstractUploader):
    def __init__(self, backend=None, **kwargs):
        if backend is None:
            backend = DocUploadBackend
        self.get_backend = lambda: backend(**kwargs)

    def _ajax_upload(self, request, **kwargs):
        if request.method == "POST":
            self._upload_file(request, **kwargs)
            if self.success:
                new = Doc()
                self._new_obj(new, request, **kwargs)
                new.file = self.extra_context['path']
                new.filetype = 0
                fullpath = os.path.join(settings.MEDIA_ROOT,
                    new.file.field.upload_to, new.file.path)
                new.size = os.path.getsize(fullpath)
                new.save()
                messages.success(request, _("File %s successfully uploaded") %
                                          new.description)
                # let Ajax Upload know whether we saved it or not
            payload = {'success': self.success, 'filename': self.filename}
            if self.extra_context is not None:
                payload.update(self.extra_context)
            return AjaxAnswer(payload)


class AjaxImageUploader(AjaxAbstractUploader):
    def __init__(self, backend=None, **kwargs):
        if backend is None:
            backend = PicUploadBackend
        self.get_backend = lambda: backend(**kwargs)

    def _ajax_upload(self, request, **kwargs):
        if request.method == "POST":
            self._upload_file(request, **kwargs)
            fullpath = os.path.join(settings.MEDIA_ROOT,
                self.extra_context['path'])
            try:
                i = Image.open(fullpath)
            except:
                messages.error(request, "File is not image format")
                os.remove(fullpath)
                self.success = False
            if self.success:
                new = Pic()
                self._new_obj(new, request, **kwargs)
                new.pic = self.extra_context['path']
                fullpath = os.path.join(settings.MEDIA_ROOT,
                    new.pic.field.upload_to, new.pic.path)
                new.size = os.path.getsize(fullpath)
                new.save()
                messages.success(request, _("Image %s successfully uploaded") %
                            new.description)
                # let Ajax Upload know whether we saved it or not
            payload = {'success': self.success, 'filename': self.filename}
            if self.extra_context is not None:
                payload.update(self.extra_context)
            return AjaxAnswer(payload)

class AjaxAvatarUploader(AjaxAbstractUploader):
    def __init__(self, backend=None, **kwargs):
        if backend is None:
            backend = AvatarUploadBackend
        self.get_backend = lambda: backend(**kwargs)

    def _ajax_upload(self, request, **kwargs):
        if request.method == "POST":
            self._upload_file(request, **kwargs)
            fullpath = os.path.join(settings.MEDIA_ROOT,
                self.extra_context['path'])
            try:
                i = Image.open(fullpath)
            except:
                messages.error(request, "File is not image format")
                os.remove(fullpath)
                self.success = False
            if self.success:
                profile = request.user.get_profile()
                try:
                    remove_thumbnails(profile.avatar.url)
                    remove_file(profile.avatar.url)
                except :
                    pass
                profile.avatar = self.extra_context['path']
                profile.avatar_complete = False
                profile.save()
                resize_image(profile.avatar.url)
                messages.success(request, _("Avatar %s successfully uploaded"))
                # let Ajax Upload know whether we saved it or not
            payload = {'success': self.success, 'filename': self.filename}
            if self.extra_context is not None:
                payload.update(self.extra_context)
            return AjaxAnswer(payload)


def as_json(errors):
    return dict((k, map(unicode, v)) for k, v in errors.items())

