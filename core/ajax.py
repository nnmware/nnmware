# -*- coding: utf-8 -*-

from io import FileIO, BufferedWriter
from hashlib import md5
import os
import shutil
from PIL import Image
import json
import copy
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import linebreaksbr
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from nnmware.core.constants import STATUS_LOCKED, ACTION_LIKED, ACTION_COMMENTED, ACTION_FOLLOWED
from nnmware.core import oembed
from nnmware.core.actions import unfollow, follow
from nnmware.core.exceptions import AccessError
from nnmware.core.file import get_path_from_url
from nnmware.core.http import LazyEncoder
from nnmware.core.models import Pic, Doc, Video, Follow, Tag, Notice, Message, \
    Nnmcomment, FlatNnmcomment, Like
from nnmware.core.imgutil import remove_thumbnails, remove_file, make_thumbnail
from nnmware.core.signals import notice, action
from nnmware.core.utils import update_video_size, setting, get_date_directory


def ajax_answer(payload):
    return HttpResponse(json.dumps(payload), content_type='application/json')


def ajax_answer_lazy(payload):
    return HttpResponse(json.dumps(payload, cls=LazyEncoder), content_type='application/json')


# class AjaxAbstractUploader(object):
#     def __call__(self, request, **kwargs):
#         return self._ajax_upload(request, **kwargs)
#
#     def _ajax_upload(self, request, **kwargs):
#         raise NotImplemented
#
#     def get_backend(self):
#         raise NotImplemented
#
#     def _upload_file(self, request, **kwargs):
#         if request.is_ajax():
#             # the file is stored raw in the request
#             self.upload = request
#             self.is_raw = True
#             # AJAX Upload will pass the filename in the querystring if it
#             # is the "advanced" ajax upload
#             try:
#                 self.filename = request.GET['qqfile']
#             except KeyError:
#                 return HttpResponseBadRequest("AJAX request not valid")
#                 # not an ajax upload, so it was the "basic" iframe version with
#                 # submission via form
#         else:
#             self.is_raw = False
#             if len(request.FILES) == 1:
#                 # FILES is a dictionary in Django but Ajax Upload gives
#                 # the uploaded file an ID based on a random number, so it
#                 # cannot be guessed here in the code. Rather than editing
#                 # Ajax Upload to pass the ID in the querystring, observe
#                 # that each upload is a separate request, so FILES should
#                 # only have one entry. Thus, we can just grab the first
#                 # (and only) value in the dict.
#                 self.upload = request.FILES.values()[0]
#             else:
#                 raise Http404("Bad Upload")
#             self.filename = self.upload.name
#         backend = self.get_backend()
#
#         # custom filename handler
#         self.filename = (backend.update_filename(request, self.filename)
#                          or self.filename)
#         # save the file
#         backend.setup(self.filename)
#         self.success = backend.upload(self.upload, self.filename, self.is_raw)
#         # callback
#         self.extra_context = backend.upload_complete(request, self.filename)
#
#     def _new_obj(self, target, request, **kwargs):
#         target.content_type = get_object_or_404(ContentType, id=int(kwargs['content_type']))
#         target.object_id = int(kwargs['object_id'])
#         target.description = self.extra_context['oldname']
#         target.user = request.user
#         target.created_date = now()


# class AjaxFileUploader(AjaxAbstractUploader):
#     def __init__(self, backend=None, **kwargs):
#         if backend is None:
#             backend = DocUploadBackend
#         self.get_backend = lambda: backend(**kwargs)
#
#     def _ajax_upload(self, request, **kwargs):
#         if request.method == "POST":
#             self._upload_file(request, **kwargs)
#             if self.success:
#                 new = Doc()
#                 self._new_obj(new, request, **kwargs)
#                 new.file = self.extra_context['path']
#                 new.filetype = 0
#                 fullpath = os.path.join(settings.MEDIA_ROOT,
#                                         new.file.field.upload_to, new.file.path)
#                 new.size = os.path.getsize(fullpath)
#                 new.save()
#                 messages.success(request, _("File %s successfully uploaded") % new.description)
#                 # let Ajax Upload know whether we saved it or not
#             payload = {'success': self.success, 'filename': self.filename}
#             if self.extra_context is not None:
#                 payload.update(self.extra_context)
#             return ajax_answer(payload)


# class AjaxImageUploader(AjaxAbstractUploader):
#     # TODO Later is deprecated
#     def __init__(self, backend=None, **kwargs):
#         if backend is None:
#             backend = ImgUploadBackend
#         self.get_backend = lambda: backend(**kwargs)
#
#     def _ajax_upload(self, request, **kwargs):
#         if request.method == "POST":
#             self._upload_file(request, **kwargs)
#             fullpath = os.path.join(settings.MEDIA_ROOT,
#                                     self.extra_context['path'])
#             try:
#                 i = Image.open(fullpath)
#             except:
#                 messages.error(request, "File is not image format")
#                 os.remove(fullpath)
#                 self.success = False
#                 self.pic_id = None
#                 addons = None
#             if self.success:
#                 new = Pic()
#                 self._new_obj(new, request, **kwargs)
#                 new.pic = self.extra_context['path']
#                 fullpath = os.path.join(settings.MEDIA_ROOT,
#                                         new.pic.field.upload_to, new.pic.path)
#                 new.size = os.path.getsize(fullpath)
#                 new.save()
#                 self.pic_id = new.pk
#                 # let Ajax Upload know whether we saved it or not
#                 addons = {'size': os.path.getsize(fullpath),
#                           'thumbnail': make_thumbnail(new.pic.url, width=settings.DEFAULT_THUMBNAIL_WIDTH,
#                                                       height=settings.DEFAULT_THUMBNAIL_HEIGHT, aspect=1)}
#             payload = {'success': self.success, 'filename': self.filename, 'id': self.pic_id}
#             if self.extra_context is not None:
#                 payload.update(self.extra_context)
#             if addons:
#                 payload.update(addons)
#             return ajax_answer(payload)


# class AjaxAvatarUploader(AjaxAbstractUploader):
#     # TODO Later is deprecated
#     def __init__(self, backend=None, **kwargs):
#         if backend is None:
#             backend = AvatarUploadBackend
#         self.get_backend = lambda: backend(**kwargs)
#
#     def _ajax_upload(self, request, **kwargs):
#         if request.method == "POST":
#             self._upload_file(request, **kwargs)
#             fullpath = os.path.join(settings.MEDIA_ROOT,
#                                     self.extra_context['path'])
#             try:
#                 i = Image.open(fullpath)
#             except:
#                 messages.error(request, "File is not image format")
#                 os.remove(fullpath)
#                 self.success = False
#                 self.pic_id = None
#             if self.success:
#                 try:
#                     request.user.img.delete()
#                 except:
#                     pass
#                 new = Pic()
#                 new.content_type = ContentType.objects.get_for_model(get_user_model())
#                 new.object_id = request.user.pk
#                 new.description = self.extra_context['oldname']
#                 new.user = request.user
#                 new.created_date = now()
#                 new.pic = self.extra_context['path']
#                 new.save()
#                 request.user.img = new
#                 request.user.save()
#                 self.pic_id = new.pk
#                 # let Ajax Upload know whether we saved it or not
#             payload = {'success': self.success, 'filename': self.filename, 'id': self.pic_id}
#             if self.extra_context is not None:
#                 payload.update(self.extra_context)
#             return ajax_answer(payload)


# class AjaxImgUploader(AjaxAbstractUploader):
#     # TODO Later is deprecated
#     def __init__(self, backend=None, **kwargs):
#         if backend is None:
#             backend = ImgUploadBackend
#         self.get_backend = lambda: backend(**kwargs)
#
#     def _ajax_upload(self, request, **kwargs):
#         if request.method == "POST":
#             tmb = None
#             self._upload_file(request, **kwargs)
#             fullpath = os.path.join(settings.MEDIA_ROOT, self.extra_context['path'])
#             try:
#                 i = Image.open(fullpath)
#             except:
#                 messages.error(request, "File is not image format")
#                 os.remove(fullpath)
#                 self.success = False
#                 self.pic_id = None
#             if self.success:
#                 ctype = get_object_or_404(ContentType, id=int(kwargs['content_type']))
#                 object_id = int(kwargs['object_id'])
#                 obj = ctype.get_object_for_this_type(pk=object_id)
#                 try:
#                     remove_thumbnails(obj.img.path)
#                     remove_file(obj.img.path)
#                     obj.img.delete()
#                 except:
#                     pass
#                 obj.img = self.extra_context['path']
#                 obj.save()
#                 # let Ajax Upload know whether we saved it or not
#                 addons = {'tmb': make_thumbnail(obj.img.url, width=int(kwargs['width']), height=int(kwargs['height']),
#                                                 aspect=int(kwargs['aspect']))}
#             payload = {'success': self.success, 'filename': self.filename}
#             if self.extra_context is not None:
#                 payload.update(self.extra_context)
#             if addons:
#                 payload.update(addons)
#             return ajax_answer(payload)


def as_json(errors):
    return dict((k, map(unicode, v)) for k, v in errors.items())


def img_check_rights(request, obj):
    if request.user.is_superuser:
        return True
    return False


def img_setmain(request, object_id, img_w='64', img_h='64'):
    # Link used for User press SetMain for Image
    pic = get_object_or_404(Pic, id=int(object_id))
    if img_check_rights(request, pic):
        all_pics = Pic.objects.for_object(pic.content_object)
        all_pics.update(primary=False)
        pic.primary = True
        pic.save()
        payload = {'success': True, 'src': make_thumbnail(pic.pic.url, width=int(img_w), height=int(img_h), aspect=1)}
    else:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def img_delete(request, object_id):
    # Link used for User press Delete for Image
    pic = get_object_or_404(Pic, id=int(object_id))
    if img_check_rights(request, pic):
        pic.delete()
        payload = {'success': True}
    else:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def img_getcrop(request, object_id):
    # Link used for User want crop image
    pic = get_object_or_404(Pic, id=int(object_id))
    try:
        payload = dict(success=True, src=make_thumbnail(pic.pic.url, width=settings.MAX_IMAGE_CROP_WIDTH), id=pic.pk)
    except:
        payload = dict(success=False)
    return ajax_answer_lazy(payload)


def img_rotate(request):
    # Rotate image
    try:
        if not request.user.is_superuser:
            raise AccessError
        img_pk = request.POST['crop_id']
        pic = get_object_or_404(Pic, id=int(img_pk))
        img = get_path_from_url(pic.pic.url)
        im = Image.open(img)
        im = im.rotate(90)
        if im.mode not in ('L', 'RGB'):
            im = im.convert('RGB')
        im.save(img)
        pic.save()
        payload = {'success': True, 'id': pic.pk}
    except AccessError:
        payload = {'success': False, 'error': _('You are not allowed rotate this image')}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


@login_required
def avatardelete(request):
    if request.is_ajax():
        try:
            u = request.user
            remove_thumbnails(u.img.path)
            remove_file(u.img.path)
            u.avatar_complete = False
            u.img = None
            u.save()
            payload = {'success': True}
        except:
            payload = {'success': False}
        return ajax_answer_lazy(payload)
    else:
        raise Http404()


def get_video(request):
    link = request.POST['link']
    if not link[:7] == 'http://':
        link = 'http://%s' % link
    if link.find('youtu.be') != -1:
        link = link.replace('youtu.be/', 'www.youtube.com/watch?v=')
    try:
        search_qs = Video.objects.filter(video_url=link)[0]
    except:
        search_qs = False
    if search_qs:
        payload = dict(success=False, location=search_qs.get_absolute_url())
    else:  # try:
        consumer = oembed.OEmbedConsumer(link)
        result = consumer.result()
        if result is not None:
            result['html'] = update_video_size(result['html'], 500, 280)
        payload = {'success': True, 'data': result}
        #    except:
    #        payload = {'success': False}
    return ajax_answer_lazy(payload)


def push_video(request, object_id):
    # Link used for User press Like on Video Detail Page
    try:
        video = get_object_or_404(Video, id=int(object_id))
        ctype = ContentType.objects.get_for_model(Video)
        status = False
        if Follow.objects.filter(user=request.user, content_type=ctype, object_id=object_id).count():
            if unfollow(request.user, video):
            #                action.send(request.user, verb=_('disliked the video'), target=video)
                if request.user.followers_count:
                    for u in get_user_model().objects.filter(pk__in=request.user.followers):
                        notice.send(request.user, user=u, verb=_('now disliked'), target=video)
        else:
            if follow(request.user, video):
                status = True
                action.send(request.user, verb=_('liked the video'), action_type=ACTION_LIKED,
                            target=video, request=request)
                if request.user.followers_count:
                    for u in get_user_model().objects.filter(pk__in=request.user.followers):
                        if u.follow_set.filter(content_type=ctype, object_id=video.pk).count:
                            notice.send(request.user, user=u, verb=_('also now liked'), target=video)
                        else:
                            notice.send(request.user, user=u, verb=_('now liked'), target=video)
        result = Follow.objects.filter(content_type=ctype, object_id=object_id).count()
        payload = {'success': True, 'count': result, 'id': video.pk, 'status': status}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def push_tag(request, object_id):
    # Link used for User follow tag
    try:
        tag = Tag.objects.get(id=object_id)
        ctype = ContentType.objects.get_for_model(Tag)
        status = False
        if Follow.objects.filter(user=request.user, content_type=ctype, object_id=object_id).count():
            unfollow(request.user, tag)
            action.send(request.user, verb=_('unfollow the tag'), target=tag)
            if request.user.followers_count:
                for u in get_user_model().objects.filter(pk__in=request.user.followers):
                    notice.send(request.user, user=u, verb=_('now follow'), target=tag)
        else:
            follow(request.user, tag)
            status = True
            action.send(request.user, verb=_('follow the tag'), action_type=ACTION_FOLLOWED, target=tag,
                        request=request)
            if request.user.followers_count:
                for u in get_user_model().objects.filter(pk__in=request.user.followers):
                    if u.follow_set.filter(content_type=ctype, object_id=tag.pk).count:
                        notice.send(request.user, user=u, verb=_('also now follow'), target=tag)
                    else:
                        notice.send(request.user, user=u, verb=_('now follow'), target=tag)
        result = Follow.objects.filter(content_type=ctype, object_id=object_id).count()
        payload = {'success': True, 'count': result, 'id': tag.pk, 'status': status}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def push_notify(request):
    try:
        u = request.user
        if u.subscribe:
            u.subscribe = False
        else:
            u.subscribe = True
        u.save()
        payload = {'success': True}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def push_user(request, object_id):
    # Link used for User press button in user panel
    try:
        user = get_user_model().objects.get(id=object_id)
        if request.user == user:
            raise AccessError
        ctype = ContentType.objects.get_for_model(get_user_model())
        status = False
        if Follow.objects.filter(user=request.user, content_type=ctype, object_id=object_id).count():
            unfollow(request.user, user)
            action.send(request.user, verb=_('unfollow the user'), target=user)
            if request.user.followers_count:
                for u in get_user_model().objects.filter(pk__in=request.user.followers):
                    notice.send(request.user, user=u, verb=_('now unfollow'), target=user)
        else:
            follow(request.user, user)
            status = True
            action.send(request.user, verb=_('follow the user'), target=user)
            if request.user.followers_count:
                for u in get_user_model().objects.filter(pk__in=request.user.followers):
                    if u.follow_set.filter(content_type=ctype, object_id=user.pk).count:
                        notice.send(request.user, user=u, verb=_('also now follow'), target=user)
                    else:
                        notice.send(request.user, user=u, verb=_('now follow'), target=user)
        result = Follow.objects.filter(content_type=ctype, object_id=object_id).count()
        payload = {'success': True, 'count': result, 'id': user.pk, 'status': status}
    except AccessError:
        payload = {'success': False}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def follow_object(request, content_type_id, object_id):
    """
    Creates the follow relationship between ``request.user`` and the
    actor defined by ``content_type_id``, ``object_id``.
    """
    ctype = get_object_or_404(ContentType, id=content_type_id)
    if not Follow.objects.filter(user=request.user, content_type=ctype, object_id=object_id).count():
        actor = ctype.get_object_for_this_type(id=object_id)
        follow(request.user, actor)
        success = True
    else:
        success = False
    count = Follow.objects.filter(content_type=ctype, object_id=object_id).count()
    payload = {'success': success, 'count': count}
    return ajax_answer_lazy(payload)


def unfollow_object(request, content_type_id, object_id):
    """
    Creates the follow relationship between ``request.user`` and the
    actor defined by ``content_type_id``, ``object_id``.
    """
    ctype = get_object_or_404(ContentType, id=content_type_id)
    if Follow.objects.filter(user=request.user, content_type=ctype, object_id=object_id).count():
        actor = ctype.get_object_for_this_type(id=object_id)
        unfollow(request.user, actor, send_action=True)
        success = True
    else:
        success = False
    count = Follow.objects.filter(content_type=ctype, object_id=object_id).count()
    payload = {'success': success, 'count': count}
    return ajax_answer_lazy(payload)


def follow_unfollow(request, content_type, object_id):
    count = None
    try:
        ctype = get_object_or_404(ContentType, id=content_type)
        follow_count = Follow.objects.filter(user=request.user, content_type=ctype, object_id=object_id).count()
        actor = ctype.get_object_for_this_type(id=object_id)
        if not follow_count:
            follow(request.user, actor)
        else:
            unfollow(request.user, actor, send_action=True)
        count = Follow.objects.filter(content_type=ctype, object_id=object_id).count()
        success = True
    except:
        success = False
    payload = {'success': success, 'count': count}
    return ajax_answer_lazy(payload)


def autocomplete_users(request):
    search_qs = get_user_model().objects.filter(username__icontains=request.POST['q'])
    results = []
    for r in search_qs:
        userstring = {'name': r.username, 'fullname': r.fullname}
        results.append(userstring)
    payload = {'userlist': results}
    return ajax_answer_lazy(payload)


def autocomplete_tags(request):
    search_qs = Tag.objects.filter(name__icontains=request.POST['q'])
    results = []
    for r in search_qs:
        results.append(r.name)
    payload = {'q': results}
    return ajax_answer_lazy(payload)


# doc_uploader = AjaxFileUploader()
# TODO Later is deprecated
# pic_uploader = AjaxImageUploader()
# avatar_uploader = AjaxAvatarUploader()
# img_uploader = AjaxImgUploader()


def notice_delete(request, object_id):
    # Link used when User delete the notification
    if Notice.objects.get(user=request.user, id=object_id):
        Notice.objects.get(user=request.user, id=object_id).delete()
        result = Notice.objects.filter(user=request.user).count()
        payload = {'success': True, 'count': result}
    else:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def delete_message(request, object_id):
    # Link used when User delete the Message
    msg = None
    if Message.objects.filter(sender=request.user, id=object_id).count():
        msg = Message.objects.get(sender=request.user, id=object_id)
        another_user = msg.recipient
        msg.sender_deleted_at = now()
    elif Message.objects.filter(recipient=request.user, id=object_id).count():
        msg = Message.objects.get(recipient=request.user, id=object_id)
        another_user = msg.sender
        msg.recipient_deleted_at = now()
    if msg is not None:
        msg.save()
        result = Message.objects.concrete_user(request.user, another_user).count()
        payload = {'success': True, 'count': result}
    else:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def avatar_delete(request):
    try:
        u = request.user
        remove_thumbnails(u.img.url)
        remove_file(u.img.url)
        u.img = ''
        u.save()
        payload = {'success': True}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def message_add(request):
    """
    Message add ajax
    """
    recipients = request.POST['recipients'].strip().split(',')
    recipients = filter(None, recipients)  # Remove empty values
    try:
        for u in recipients:
            user = get_user_model().objects.get(username=u)
            if user and (user != request.user):
                m = Message()
                m.recipient = user
                m.sent_at = now()
                m.sender = request.user
                m.body = request.POST['body']
                m.save()
        success = True
    except:
        success = False
    location = reverse('user_messages')
    payload = {'success': success, 'location': location}
    return ajax_answer_lazy(payload)


def message_user_add(request):
    user = get_object_or_404(get_user_model(), username=request.POST['user'])
    result = dict()
    result['fullname'] = user.get_name()
    result['url'] = user.get_absolute_url()
    result['username'] = user.username
    result['id'] = user.pk
    if user.img:
        result['avatar_url'] = user.img.url
    else:
        result['avatar_url'] = '/m/generic_t30.jpg'
    payload = {'success': True, 'data': result}
    #    except:
    #        payload = {'success': False}
    return ajax_answer_lazy(payload)


def pic_delete(request, object_id):
    # Link used for User press Delete for Image
    pic = get_object_or_404(Pic, id=int(object_id))
    try:
        pic.delete()
        payload = {'success': True}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def pic_setmain(request, object_id):
    # TODO check user rights!!
    # Link used for User press SetMain for Image
    try:
        pic = Pic.objects.get(id=int(object_id))
        all_pics = Pic.objects.for_object(pic.content_object)
        all_pics.update(primary=False)
        pic.primary = True
        pic.save()
        payload = {'success': True}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def doc_delete(request, object_id):
    # Link used for User press Delete for Image
    doc = get_object_or_404(Doc, id=int(object_id))
    try:
        doc.delete()
        payload = {'success': True}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def pic_getcrop(request, object_id):
    # Link used for User want crop image
    pic = get_object_or_404(Pic, id=int(object_id))
    try:
        payload = dict(success=True, src=make_thumbnail(pic.pic.url, width=settings.MAX_IMAGE_CROP_WIDTH), id=pic.pk)
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def AjaxGetThumbnail(request):
    img_pk = int(request.POST['image_id'])
    pic = get_object_or_404(Pic, id=int(img_pk))
    width = request.POST.get('width') or None
    height = request.POST.get('height') or None
    if width:
        width = int(width)
    if height:
        height = int(height)
    try:
        payload = dict(success=True, src=make_thumbnail(pic.pic.url, width=width, height=height), id=pic.pk)
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def ajax_image_crop(request):
    # Crop image
    try:
        img_pk = request.POST['crop_id']
        pic = get_object_or_404(Pic, id=int(img_pk))
        if not request.user.is_superuser:
            parent_object = pic.content_object.__class__.__name__
            if parent_object == 'Room':
                if not request.user in pic.content_object.hotel.admins.all():
                    raise AccessError
            elif parent_object == 'Hotel':
                if not request.user in pic.content_object.admins.all():
                    raise AccessError
        left = int(request.POST['crop_x1'])
        right = int(request.POST['crop_x2'])
        top = int(request.POST['crop_y1'])
        bottom = int(request.POST['crop_y2'])
        box = [left, top, right, bottom]
        img = get_path_from_url(pic.pic.url)
        im = Image.open(img)
        if im.size[0] > settings.MAX_IMAGE_CROP_WIDTH:
            aspect_c = float(im.size[0]) / settings.MAX_IMAGE_CROP_WIDTH
            box = map(lambda x: int(x * aspect_c), box)
        im = im.crop(box)
        if im.mode not in ('L', 'RGB'):
            im = im.convert('RGB')
        im.save(img)
        pic.save()
        payload = {'success': True, 'id': pic.pk}
    except AccessError:
        payload = {'success': False, 'error': _('You are not allowed change this image')}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def comment_add_oldver(request, content_type, object_id, parent_id=None):
    """
    Its Ajax posted comments
    """
    try:
        if not request.user.is_authenticated():
            raise AccessError
        comment = Nnmcomment()
        comment.user = request.user
        comment.content_type = get_object_or_404(ContentType, id=int(content_type))
        comment.object_id = int(object_id)
        comment.ip = request.META['REMOTE_ADDR']
        comment.user_agent = request.META['HTTP_USER_AGENT']
        comment.comment = request.POST['comment']
        if not len(comment.comment):
            raise AccessError
        kwargs = {'content_type': content_type, 'object_id': object_id}
        if parent_id is not None:
            comment.parent_id = int(parent_id)
        comment.save()
        action.send(request.user, verb=_('commented'), action_type=ACTION_COMMENTED,
                    description=comment.comment, target=comment.content_object, request=request)
        avatar_id = False
        kwargs['parent_id'] = comment.pk
        reply_link = reverse("jcomment_parent_add", kwargs=kwargs)
        comment_text = linebreaksbr(comment.comment)
        comment_date = comment.created_date.strftime(settings.COMMENT_DATE_FORMAT)
        try:
            avatar_id = comment.user.avatar.pk
        except:
            pass
        payload = {'success': True, 'id': comment.pk, 'username': comment.user.get_name,
                   'username_url': comment.get_absolute_url(),
                   'comment': comment_text, 'avatar_id': avatar_id,
                   'comment_date': comment_date, 'reply_link': reply_link,
                   'object_comments': comment.content_object.comments}
    except AccessError:
        payload = {'success': False, 'error': _('You are not allowed for add comment')}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def comment_add(request, content_type, object_id, parent_id=None):
    try:
        if not request.user.is_authenticated():
            raise AccessError
        comment = Nnmcomment()
        comment.user = request.user
        comment.content_type = get_object_or_404(ContentType, id=int(content_type))
        comment.object_id = int(object_id)
        comment.ip = request.META['REMOTE_ADDR']
        comment.user_agent = request.META['HTTP_USER_AGENT']
        comment.comment = request.REQUEST['comment'] or None
        depth = int(request.REQUEST['depth'])
        if len(comment.comment) < 1:
            raise AccessError
        if parent_id is not None:
            comment.parent_id = int(parent_id)
        comment.save()
        action.send(request.user, verb=_('commented'), action_type=ACTION_COMMENTED,
                    description=comment.comment, target=comment.content_object, request=request)
        newcomment = copy.deepcopy(comment)
        newcomment.depth = depth
        html = render_to_string('comments/comment_one.html', {'comment': newcomment, 'user': request.user})
        payload = {'success': True, 'html': html, 'object_comments': comment.content_object.comments}
    except AccessError:
        payload = {'success': False, 'error': 'You are not allowed for add comment'}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def flat_comment_add(request, content_type, object_id):
    """
    Its Ajax flat posted comments
    """
    try:
        if not request.user.is_authenticated():
            raise AccessError
        comment = FlatNnmcomment()
        comment.user = request.user
        comment.content_type = get_object_or_404(ContentType, id=int(content_type))
        comment.object_id = int(object_id)
        comment.ip = request.META['REMOTE_ADDR']
        comment.user_agent = request.META['HTTP_USER_AGENT']
        comment.comment = request.POST['comment']
        if not len(comment.comment):
            raise AccessError
        kwargs = {'content_type': content_type, 'object_id': object_id}
        comment.save()
        action.send(request.user, verb=_('commented'), action_type=ACTION_COMMENTED,
                    description=comment.comment, target=comment.content_object, request=request)
        html = render_to_string('comments/item_comment.html', {'comment': comment})
        payload = {'success': True, 'html': html}
    except AccessError:
        payload = {'success': False, 'error': _('You are not allowed for add comment')}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def push_message(request, pk):
    if 1>0: #try:
        if not request.user.is_authenticated():
            raise AccessError
        recipient = get_user_model().objects.get(pk=pk)
        if recipient == request.user:
            raise AccessError
        body = request.POST.get('message') or None
        if body is None:
            raise AccessError
        msg = Message()
        msg.subject = request.POST.get('subject') or ''
        msg.ip = request.META['REMOTE_ADDR']
        msg.user_agent = request.META['HTTP_USER_AGENT']
        msg.body = body
        msg.sender = request.user
        msg.recipient = recipient
        msg.sent_at = now()
        msg.save()
        result = Message.objects.concrete_user(request.user, recipient).count()
        html = render_to_string('user/one_message.html', {'object': msg, 'user': request.user})
        payload = {'success': True, 'html': html, 'count': result, 'id': recipient.pk,
                   'total': request.user.messages_count}
    # except AccessError:
    #     payload = {'success': False, 'error': 'You are not allowed for send message'}
    # except:
    #     payload = {'success': False}
    return ajax_answer_lazy(payload)


def set_paginator(request, num):
    try:
        request.session['paginator'] = num
        payload = {'success': True}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


class AjaxUploader(object):
    BUFFER_SIZE = 10485760  # 10MB

    def __init__(self, filetype='file', upload_dir='files', size_limit=10485760):
        self._upload_dir = os.path.join(settings.MEDIA_ROOT, upload_dir, get_date_directory())
        self._filetype = filetype
        if filetype == 'image':
            self._save_format = setting('IMAGE_UPLOAD_FORMAT', 'JPEG')
        else:
            self._save_format = None
        self._size_limit = size_limit

    def max_size(self):
        """
        Checking file max size
        """
        if int(self._destination.tell()) > self._size_limit:
            self._destination.close()
            os.remove(self._path)
            return True

    def setup(self, filename):
        ext = os.path.splitext(filename)[1]
        self._filename = md5(filename.encode('utf8')).hexdigest() + ext
        self._path = os.path.join(self._upload_dir, self._filename)
        try:
            os.makedirs(os.path.realpath(os.path.dirname(self._path)))
        except:
            pass
        self._destination = BufferedWriter(FileIO(self._path, "w"))

    def handle_upload(self, request):
        is_raw = True
        if request.FILES:
            is_raw = False
            if len(request.FILES) == 1:
                upload = request.FILES.values()[0]
            else:
                return dict(success=False, error=_("Bad upload."))
            filename = upload.name
        else:
            # the file is stored raw in the request
            upload = request
            #get file size
            try:
                filename = request.GET['qqfile']
            except KeyError:
                return dict(success=False, error=_("Can't read file name"))
        self.setup(filename)
        try:
            if is_raw:
                # File was uploaded via ajax, and is streaming in.
                chunk = upload.read(self.BUFFER_SIZE)
                while len(chunk) > 0:
                    self._destination.write(chunk)
                    if self.max_size():
                        raise
                    chunk = upload.read(self.BUFFER_SIZE)
            else:
                # File was uploaded via a POST, and is here.
                for chunk in upload.chunks():
                    self._destination.write(chunk)
                    if self.max_size():
                        raise
        except:
            # things went badly.
            return dict(success=False, error=_("Upload error"))
        self._destination.close()
        if self._filetype == 'image':
            try:
                i = Image.open(self._path)
            except:
                os.remove(self._path)
                return dict(success=False, error=_("File is not image format"))
            f_name, f_ext = os.path.splitext(self._filename)
            f_without_ext = os.path.splitext(self._path)[0]
            new_path = ".".join([f_without_ext, self._save_format.lower()])
            if setting('IMAGE_STORE_ORIGINAL', False):
                # TODO need change the extension
                orig_path = ".".join([f_without_ext + '_orig', self._save_format.lower()])
                shutil.copy2(self._path, orig_path)
            i.thumbnail((1200, 1200), Image.ANTIALIAS)
            try:
                if self._path == new_path:
                    i.save(self._path, self._save_format)
                else:
                    i.save(new_path, self._save_format)
                    os.remove(self._path)
                    self._path = new_path
            except:
                try:
                    os.remove(self._path)
                    os.remove(new_path)
                except:
                    pass
                return dict(success=False, error=_("Error saving image"))
            self._filename = ".".join([f_name, self._save_format.lower()])
        return dict(success=True, fullpath=self._path, path=os.path.relpath(self._path, '/' + settings.MEDIA_ROOT),
                    old_filename=filename, filename=self._filename)


def file_uploader(request, **kwargs):
    uploader = AjaxUploader(filetype='image', upload_dir=setting('IMAGE_UPLOAD_DIR', 'images'),
                            size_limit=setting('IMAGE_UPLOAD_SIZE', 10485760))
    result = uploader.handle_upload(request)
    if result['success']:
        ctype = get_object_or_404(ContentType, id=int(kwargs['content_type']))
        object_id = int(kwargs['object_id'])
        obj = ctype.get_object_for_this_type(pk=object_id)
        try:
            remove_thumbnails(obj.img.path)
            remove_file(obj.img.path)
            obj.img.delete()
        except:
            pass
        obj.img = result['path']
        obj.save()
        try:
            addons = dict(tmb=make_thumbnail(obj.img.url, width=int(kwargs['width']), height=int(kwargs['height']),
                                             aspect=int(kwargs['aspect'])))
        except:
            addons = {}
        result.update(addons)
    return ajax_answer(result)


def addon_image_uploader(request, **kwargs):
    uploader = AjaxUploader(filetype='image', upload_dir=setting('IMAGE_UPLOAD_DIR', 'images'),
                            size_limit=setting('IMAGE_UPLOAD_SIZE', 10485760))
    result = uploader.handle_upload(request)
    if result['success']:
        new = Pic()
        new.content_type = get_object_or_404(ContentType, id=int(kwargs['content_type']))
        new.object_id = int(kwargs['object_id'])
        new.description = result['old_filename']
        new.user = request.user
        new.created_date = now()
        new.pic = result['path']
        fullpath = os.path.join(settings.MEDIA_ROOT,
                                new.pic.field.upload_to, new.pic.path)
        new.size = os.path.getsize(fullpath)
        new.save()
        try:
            pics_count = dict(pics_count=new.content_object.pics_count)
            result.update(pics_count)
        except:
            pass
        try:
            addons = dict(html=render_to_string('upload/image_item.html', {'pic': new}))
        except:
            addons = {}
        result.update(addons)
    return ajax_answer(result)


def like(request, content_type, object_id):
    try:
        if not request.user.is_authenticated():
            raise AccessError
        mode = request.POST['mode']
        content_type = get_object_or_404(ContentType, id=int(content_type))
        object_id = int(object_id)
        if content_type == ContentType.objects.get_for_model(get_user_model()):
            if object_id == request.user.pk:
                raise AccessError
        try:
            thelike = Like.objects.get(user=request.user, content_type=content_type, object_id=object_id)
        except:
            thelike = Like(user=request.user, content_type=content_type, object_id=object_id)
            thelike.save()
        if mode == 'like':
            if not thelike.like:
                thelike.like = True
                thelike.dislike = False
                like_en = True
            else:
                thelike.like = False
                like_en = False
            dislike_en = False
        else:
            if not thelike.dislike:
                thelike.dislike = True
                thelike.like = False
                dislike_en = True
            else:
                thelike.dislike = False
                dislike_en = False
            like_en = False
        thelike.save()
        karma = thelike.content_object.karma()
        payload = {'success': True, 'karma': karma, 'liked': like_en, 'disliked': dislike_en}
    except AccessError:
        payload = {'success': False, 'error': 'Not allowed'}
    except:
        payload = {'success': False}
    return ajax_answer_lazy(payload)


def delete_comment(request, object_id):
    payload = {'success': False}
    try:
        if not request.user.is_authenticated:
            raise AccessError
        comment = Nnmcomment.objects.get(pk=int(object_id))
        if comment.user == request.user or request.user.is_superuser:
            comment.status = STATUS_LOCKED
            comment.save()
            html = render_to_string('comments/comment_one.html', {'comment': comment, 'user': request.user})
            payload = {'success': True, 'html': html, 'object_comments': comment.content_object.comments}
        else:
            raise AccessError
    except AccessError:
        pass
    except:
        pass
    return ajax_answer_lazy(payload)


def avatar_set(request):
    uploader = AjaxUploader(filetype='image', upload_dir=setting('AVATAR_UPLOAD_DIR','avatars'),
                            size_limit=setting('AVATAR_UPLOAD_SIZE', 1024000))
    result = uploader.handle_upload(request)
    if result['success']:
        request.user.img = result['path']
        request.user.save()
        try:
            addons = dict(html=render_to_string('user/avatar.html', {'object': request.user}))
        except:
            addons = {}
        result.update(addons)
    return ajax_answer_lazy(result)
