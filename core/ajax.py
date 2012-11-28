# -*- coding: utf-8 -*-
from datetime import datetime
import os
import Image
import json
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from nnmware.core.exceptions import AccessError
from nnmware.core.file import get_path_from_url
from nnmware.core.http import LazyEncoder
from nnmware.core.models import Pic, Doc
from nnmware.core.backends import PicUploadBackend,DocUploadBackend, AvatarUploadBackend
from nnmware.core.imgutil import resize_image, remove_thumbnails, remove_file, make_thumbnail


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
        target.created_date = datetime.now()


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
                self.pic_id = None
                addons = None
            if self.success:
                new = Pic()
                self._new_obj(new, request, **kwargs)
                new.pic = self.extra_context['path']
                fullpath = os.path.join(settings.MEDIA_ROOT,
                    new.pic.field.upload_to, new.pic.path)
                new.size = os.path.getsize(fullpath)
                new.save()
                self.pic_id = new.pk
                # let Ajax Upload know whether we saved it or not
                addons = {'size':os.path.getsize(fullpath),
                          'thumbnail':make_thumbnail(new.pic.url, width=settings.DEFAULT_UPLOAD_THUMBNAIL_SIZE)}
            payload = {'success': self.success, 'filename': self.filename, 'id':self.pic_id}
            if self.extra_context is not None:
                payload.update(self.extra_context)
            if addons:
                payload.update(addons)
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
                self.pic_id = None
            if self.success:
                try:
                    request.user.avatar.delete()
                except :
                    pass
                new = Pic()
                new.content_type = ContentType.objects.get_for_model(get_user_model())
                new.object_id = request.user.pk
                new.description = self.extra_context['oldname']
                new.user = request.user
                new.created_date = datetime.now()
                new.pic = self.extra_context['path']
                new.save()
                request.user.avatar = new
                request.user.save()
                self.pic_id = new.pk
                # let Ajax Upload know whether we saved it or not
            payload = {'success': self.success, 'filename': self.filename, 'id':self.pic_id}
            if self.extra_context is not None:
                payload.update(self.extra_context)
            return AjaxAnswer(payload)


def as_json(errors):
    return dict((k, map(unicode, v)) for k, v in errors.items())

def img_check_rights(request, obj):
    if request.user.is_superuser:
        return True
    return False

def img_setmain(request, object_id):
    # Link used for User press SetMain for Image
    pic = get_object_or_404(Pic, id=int(object_id))
    if img_check_rights(request,pic):
        all_pics =Pic.objects.metalinks_for_object(pic.content_object)
        all_pics.update(primary=False)
        pic.primary = True
        pic.save()
        payload = {'success': True}
    else :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def img_delete(request, object_id):
    # Link used for User press Delete for Image
    pic = get_object_or_404(Pic, id=int(object_id))
    if img_check_rights(request,pic):
        pic.delete()
        payload = {'success': True}
    else :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)


def img_getcrop(request, object_id):
    # Link used for User want crop image
    pic = get_object_or_404(Pic, id=int(object_id))
    try:
        payload = {'success': True,
                   'src': make_thumbnail(pic.pic.url,width=settings.MAX_IMAGE_CROP_WIDTH),
                   'id':pic.pk}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def img_rotate(request):
    # Rotate image
    try:
        if not request.user.is_superuser:
            raise AccessError
        img_pk = request.REQUEST['crop_id']
        pic = get_object_or_404(Pic, id=int(img_pk))
        img = get_path_from_url(pic.pic.url)
        im = Image.open(img)
        im = im.rotate(90)
        if im.mode not in ('L', 'RGB'):
            im = im.convert('RGB')
        im.save(img)
        pic.save()
        payload = {'success': True, 'id':pic.pk}
    except AccessError:
        payload = {'success': False, 'error':_('You are not allowed rotate this image')}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

@login_required
def avatardelete(request):
    if request.is_ajax():
        try:
            u = request.user
            remove_thumbnails(u.avatar.path)
            remove_file(u.avatar.path)
            u.avatar_complete = False
            u.avatar = None
            u.save()
            payload = {'success': True}
        except:
            payload = {'success': False}
        return AjaxLazyAnswer(payload)
    else:
        raise Http404()
