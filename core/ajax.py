# nnmware(c)2012-2020

from __future__ import unicode_literals
from io import FileIO, BufferedWriter
from hashlib import md5
import os
import shutil
from PIL import Image
import json
import copy

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.core.files import File
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from django.http import HttpResponse, Http404

from nnmware.core.abstract import Pic, Doc
from nnmware.core.constants import STATUS_LOCKED, ACTION_LIKED, ACTION_COMMENTED, ACTION_FOLLOWED
from nnmware.core import oembed
from nnmware.core.actions import unfollow, follow
from nnmware.core.exceptions import AccessError
from nnmware.core.file import get_path_from_url
from nnmware.core.http import LazyEncoder
from nnmware.core.models import Video, Follow, Tag, Notice, Message, Nnmcomment, FlatNnmcomment, Like
from nnmware.core.imgutil import remove_thumbnails, remove_file, make_thumbnail
from nnmware.core.signals import notice, action
from nnmware.core.utils import update_video_size, setting, get_date_directory

MAX_IMAGE_CROP_WIDTH = setting('MAX_IMAGE_CROP_WIDTH', 800)


def ajax_answer(payload):
    return HttpResponse(json.dumps(payload), content_type='application/json')


def ajax_answer_lazy(payload):
    return HttpResponse(json.dumps(payload, cls=LazyEncoder), content_type='application/json')


def as_json(errors):
    return dict((k, v) for k, v in errors.items())


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
        payload = dict(success=True, src = make_thumbnail(pic.img.url, width=int(img_w), height=int(img_h), aspect=1))
    else:
        payload = dict(success=False)
    return ajax_answer_lazy(payload)


def img_delete(request, object_id):
    # Link used for User press Delete for Image
    pic = get_object_or_404(Pic, id=int(object_id))
    c_object = pic.content_object
    if img_check_rights(request, pic):
        pic.delete()
        # noinspection PyBroadException
        try:
            img_count = c_object.pics_count
        except:
            img_count = 0
        payload = dict(success=True, img_count=img_count)
    else:
        payload = dict(success=False)
    return ajax_answer_lazy(payload)


def img_getcrop(request, object_id):
    # Link used for User want crop image
    pic = get_object_or_404(Pic, id=int(object_id))
    # noinspection PyBroadException
    try:
        payload = dict(success=True, src=make_thumbnail(pic.img.url, width=MAX_IMAGE_CROP_WIDTH), id=pic.pk)
    except:
        payload = dict(success=False)
    return ajax_answer_lazy(payload)


def img_rotate(request):
    # Rotate image
    # noinspection PyBroadException
    try:
        if not request.user.is_superuser:
            raise AccessError
        img_pk = request.POST['crop_id']
        pic = get_object_or_404(Pic, id=int(img_pk))
        img = get_path_from_url(pic.img.url)
        im = Image.open(img)
        im = im.rotate(90)
        if im.mode not in ('L', 'RGB'):
            im = im.convert('RGB')
        im.save(img)
        pic.save()
        payload = {'success': True, 'id': pic.pk}
    except AccessError as aerr:
        payload = dict(success=False, error=_('You are not allowed rotate this image'))
    except:
        payload = dict(success=False)
    return ajax_answer_lazy(payload)


@login_required
def avatardelete(request):
    if request.is_ajax():
        # noinspection PyBroadException
        try:
            u = request.user
            remove_thumbnails(u.img.path)
            remove_file(u.img.path)
            u.avatar_complete = False
            u.img = None
            u.save()
            payload = dict(success=True)
        except:
            payload = dict(success=False)
        return ajax_answer_lazy(payload)
    else:
        raise Http404()


def get_video(request):
    link = request.POST['link']
    if not link[:7] == 'http://':
        link = 'http://%s' % link
    if link.find('youtu.be') != -1:
        link = link.replace('youtu.be/', 'www.youtube.com/watch?v=')
    # noinspection PyBroadException
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
        payload = dict(success=True, data=result)
    return ajax_answer_lazy(payload)


def push_video(request, object_id):
    # Link used for User press Like on Video Detail Page
    # noinspection PyBroadException
    try:
        video = get_object_or_404(Video, id=int(object_id))
        ctype = ContentType.objects.get_for_model(Video)
        status = False
        if Follow.objects.filter(user=request.user, content_type=ctype, object_id=object_id).count():
            if unfollow(request.user, video):
                # action.send(request.user, verb=_('disliked the video'), target=video)
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
        payload = dict(success=True, count=result, id=video.pk, status=status)
    except:
        payload = dict(success=False)
    return ajax_answer_lazy(payload)


def push_tag(request, object_id):
    # Link used for User follow tag
    # noinspection PyBroadException
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
        payload = dict(success=True, count=result, id=tag.pk, status=status)
    except:
        payload = dict(success=False)
    return ajax_answer_lazy(payload)


def push_notify(request):
    # noinspection PyBroadException
    try:
        u = request.user
        if u.subscribe:
            u.subscribe = False
        else:
            u.subscribe = True
        u.save()
        payload = dict(success=True)
    except:
        payload = dict(success=False)
    return ajax_answer_lazy(payload)


def push_user(request, object_id):
    # Link used for User press button in user panel
    # noinspection PyBroadException
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
        payload = dict(success=True, count=result, id=user.pk, status=status)
    except AccessError as aerr:
        payload = dict(success=False)
    except:
        payload = dict(success=False)
    return ajax_answer_lazy(payload)


def follow_object(request, content_type, object_id):
    """
    Creates the follow relationship between ``request.user`` and the
    actor defined by ``content_type_id``, ``object_id``.
    """
    ctype = ContentType.objects.get_for_id(content_type)
    if not Follow.objects.filter(user=request.user, content_type=ctype, object_id=object_id).count():
        actor = ctype.get_object_for_this_type(id=object_id)
        follow(request.user, actor)
        success = True
    else:
        success = False
    count = Follow.objects.filter(content_type=ctype, object_id=object_id).count()
    payload = dict(success=success, count=count)
    return ajax_answer_lazy(payload)


def unfollow_object(request, content_type, object_id):
    """
    Creates the follow relationship between ``request.user`` and the
    actor defined by ``content_type_id``, ``object_id``.
    """
    ctype = ContentType.objects.get_for_id(content_type)
    if Follow.objects.filter(user=request.user, content_type=ctype, object_id=object_id).count():
        actor = ctype.get_object_for_this_type(id=object_id)
        unfollow(request.user, actor, send_action=True)
        success = True
    else:
        success = False
    count = Follow.objects.filter(content_type=ctype, object_id=object_id).count()
    payload = dict(success=success, count=count)
    return ajax_answer_lazy(payload)


def follow_unfollow(request, content_type, object_id):
    count = None
    # noinspection PyBroadException
    try:
        ctype = ContentType.objects.get_for_id(content_type)
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
    payload = dict(success=success, count=count)
    return ajax_answer_lazy(payload)


def autocomplete_users(request):
    search_qs = get_user_model().objects.filter(username__icontains=request.POST['q'])
    results = []
    for r in search_qs:
        userstring = dict(name=r.username, fullname=r.fullname)
        results.append(userstring)
    payload = dict(userlist=results)
    return ajax_answer_lazy(payload)


def autocomplete_tags(request):
    search_qs = Tag.objects.filter(name__icontains=request.POST['q'])
    results = []
    for r in search_qs:
        results.append(r.name)
    payload = dict(q=results)
    return ajax_answer_lazy(payload)


def notice_delete(request, object_id):
    # Link used when User delete the notification
    if Notice.objects.get(user=request.user, id=object_id):
        Notice.objects.get(user=request.user, id=object_id).delete()
        result = Notice.objects.filter(user=request.user).count()
        payload = dict(success=True, count=result)
    else:
        payload = dict(success=False)
    return ajax_answer_lazy(payload)


def delete_message(request, object_id):
    # noinspection PyBroadException
    try:
        if not request.user.is_authenticated:
            raise AccessError
        msg = Message.objects.get(id=object_id)
        if msg.sender == request.user or msg.recipient == request.user:
            if msg.sender == request.user:
                msg.sender_deleted_at = now()
                another_user = msg.recipient
            else:
                msg.recipient_deleted_at = now()
                another_user = msg.sender
            msg.save()
            result = Message.objects.concrete_user(request.user, another_user).count()
            payload = dict(success=True, count=result, id=another_user.pk, sys=request.user.messages_count)
        else:
            raise AccessError
    except:
        payload = dict(success=False)
    return ajax_answer_lazy(payload)


def message_add(request):
    """
    Message add ajax
    """
    recipients = request.POST['recipients'].strip().split(',')
    recipients = filter(None, recipients)  # Remove empty values
    # noinspection PyBroadException
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
    payload = dict(success=success, location=location)
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
    payload = dict(success=True, data=result)
    return ajax_answer_lazy(payload)


def pic_delete(request, object_id):
    # Link used for User press Delete for Image
    pic = get_object_or_404(Pic, id=int(object_id))
    # noinspection PyBroadException
    try:
        pic.delete()
        payload = dict(success=True)
    except:
        payload = dict(success=False)
    return ajax_answer_lazy(payload)


def pic_setmain(request, object_id):
    # TODO check user rights!!
    # Link used for User press SetMain for Image
    # noinspection PyBroadException
    try:
        pic = Pic.objects.get(id=int(object_id))
        all_pics = Pic.objects.for_object(pic.content_object)
        all_pics.update(primary=False)
        pic.primary = True
        pic.save()
        payload = dict(success=True)
    except:
        payload = dict(success=False)
    return ajax_answer_lazy(payload)


def doc_delete(request, object_id):
    # Link used for User press Delete for Image
    doc = get_object_or_404(Doc, id=int(object_id))
    # noinspection PyBroadException
    try:
        doc.delete()
        payload = dict(success=True)
    except:
        payload = dict(success=False)
    return ajax_answer_lazy(payload)


def pic_getcrop(request, object_id):
    # Link used for User want crop image
    pic = get_object_or_404(Pic, id=int(object_id))
    # noinspection PyBroadException
    try:
        payload = dict(success=True, src=make_thumbnail(pic.img.url, width=MAX_IMAGE_CROP_WIDTH), id=pic.pk)
    except:
        payload = dict(success=False)
    return ajax_answer_lazy(payload)


def ajax_get_thumbnail(request):
    img_pk = int(request.POST['image_id'])
    pic = get_object_or_404(Pic, id=int(img_pk))
    width = request.POST.get('width') or None
    height = request.POST.get('height') or None
    if width:
        width = int(width)
    if height:
        height = int(height)
    # noinspection PyBroadException
    try:
        payload = dict(success=True, src=make_thumbnail(pic.pic.url, width=width, height=height), id=pic.pk)
    except:
        payload = dict(success=False)
    return ajax_answer_lazy(payload)


def ajax_image_crop(request):
    # Crop image
    # noinspection PyBroadException
    try:
        img_pk = request.POST['crop_id']
        pic = get_object_or_404(Pic, id=int(img_pk))
        if not request.user.is_superuser:
            parent_object = pic.content_object.__class__.__name__
            if parent_object == 'Room':
                if request.user not in pic.content_object.hotel.admins.all():
                    raise AccessError
            elif parent_object == 'Hotel':
                if request.user not in pic.content_object.admins.all():
                    raise AccessError
        left = int(request.POST['crop_x1'])
        right = int(request.POST['crop_x2'])
        top = int(request.POST['crop_y1'])
        bottom = int(request.POST['crop_y2'])
        box = [left, top, right, bottom]
        img = get_path_from_url(pic.pic.url)
        im = Image.open(img)
        if im.size[0] > MAX_IMAGE_CROP_WIDTH:
            aspect_c = float(im.size[0]) / MAX_IMAGE_CROP_WIDTH
            box = map(lambda x: int(x * aspect_c), box)
        im = im.crop(box)
        if im.mode not in ('L', 'RGB'):
            im = im.convert('RGB')
        im.save(img)
        pic.save()
        payload = dict(success=True, id=pic.pk)
    except AccessError as aerr:
        payload = dict(success=False, error=_('You are not allowed change this image'))
    except:
        payload = dict(success=False)
    return ajax_answer_lazy(payload)


def comment_add(request, content_type, object_id, parent_id=None):
    # noinspection PyBroadException
    try:
        if not request.user.is_authenticated:
            raise AccessError
        comment = Nnmcomment()
        comment.user = request.user
        comment.content_type = ContentType.objects.get_for_id(int(content_type))
        comment.object_id = int(object_id)
        comment.ip = request.META['REMOTE_ADDR']
        comment.user_agent = request.META['HTTP_USER_AGENT']
        comment.comment = request.POST.get('comment') or None
        depth = int(request.POST.get('depth'))
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
        payload = dict(success=True, html=html, object_comments=comment.content_object.comments)
    except AccessError as aerr:
        payload = dict(success=False, error=_('You are not allowed for add comment'))
    except:
        payload = dict(success=False)
    return ajax_answer_lazy(payload)


def flat_comment_add(request, content_type, object_id):
    """
    Its Ajax flat posted comments
    """
    # noinspection PyBroadException
    try:
        if not request.user.is_authenticated:
            raise AccessError
        comment = FlatNnmcomment()
        comment.user = request.user
        comment.content_type = ContentType.objects.get_for_id(int(content_type))
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
        payload = dict(success=True, html=html)
    except AccessError as aerr:
        payload = dict(success=False, error=_('You are not allowed for add comment'))
    except:
        payload = dict(success=False)
    return ajax_answer_lazy(payload)


def push_message(request, pk):
    # noinspection PyBroadException
    try:
        if not request.user.is_authenticated:
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
        html = render_to_string('user/message_one.html', {'message': msg, 'user': request.user})
        payload = dict(success=True, html=html, count=result, id=recipient.pk, total=request.user.messages_count)
    except AccessError as aerr:
        payload = dict(success=False, error=_('You are not allowed for send message'))
    except:
        payload = dict(success=False)
    return ajax_answer_lazy(payload)


def set_paginator(request, num):
    # noinspection PyBroadException
    try:
        request.session['paginator'] = num
        payload = dict(success=True)
    except:
        payload = dict(success=False)
    return ajax_answer_lazy(payload)


class MyError(Exception):
    pass


class AjaxUploader(object):
    BUFFER_SIZE = 10485760  # 10MB

    def __init__(self, filetype='file', upload_dir='buffer_files', size_limit=10485760):
        self._upload_dir = os.path.join(upload_dir, get_date_directory())
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
            os.remove(self._fullpath)
            return True

    def setup(self, filename):
        ext = os.path.splitext(filename)[1]
        self._filename = md5(filename.encode('utf8')).hexdigest() + ext
        self._path = os.path.join(self._upload_dir, self._filename)
        self._realpath = os.path.realpath(os.path.dirname(self._path))
        # noinspection PyBroadException
        try:
            os.makedirs(self._realpath)
        except:
            pass
        self._fullpath = os.path.join(self._realpath, self._filename)
        self._destination = BufferedWriter(FileIO(self._fullpath, "w"))

    def handle_upload(self, request):
        is_raw = True
        if request.FILES:
            is_raw = False
            if len(request.FILES) == 1:
                _var, upload = request.FILES.popitem()
            else:
                return dict(success=False, error=_("Bad upload."))
            upload = upload[0]
            filename = upload.name
        else:
            # the file is stored raw in the request
            upload = request
            # get file size
            try:
                filename = request.GET['qqfile']
            except KeyError as aerr:
                return dict(success=False, error=_("Can't read file name"))
        self.setup(filename)
        # noinspection PyBroadException
        try:
            if is_raw:
                # File was uploaded via ajax, and is streaming in.
                chunk = upload.read(self.BUFFER_SIZE)
                while len(chunk) > 0:
                    self._destination.write(chunk)
                    if self.max_size():
                        raise IOError
                    chunk = upload.read(self.BUFFER_SIZE)
            else:
                # File was uploaded via a POST, and is here.
                for chunk in upload.chunks():
                    self._destination.write(chunk)
                    if self.max_size():
                        raise IOError
        except:
            # things went badly.
            return dict(success=False, error=_("Upload error"))
        self._destination.close()
        if self._filetype == 'image':
            # noinspection PyBroadException
            try:
                i = Image.open(self._fullpath)
            except Exception as err:
                os.remove(self._fullpath)
                return dict(success=False, error=_("File is not image format"))
            f_name, f_ext = os.path.splitext(self._filename)
            f_without_ext = os.path.splitext(self._fullpath)[0]
            new_path = ".".join([f_without_ext, self._save_format.lower()])
            new_url = ".".join([f_name, self._save_format.lower()])
            if setting('IMAGE_STORE_ORIGINAL', False):
                # TODO need change the extension
                orig_path = ".".join([f_without_ext + '_orig', self._save_format.lower()])
                shutil.copy2(self._fullpath, orig_path)
            i.thumbnail((1200, 1200), Image.ANTIALIAS)
            # noinspection PyBroadException
            try:
                if self._fullpath != new_path:
                    os.remove(self._fullpath)
                    self._fullpath = new_path
                else:
                    pass
                i.save(self._fullpath, self._save_format)
            except:
                # noinspection PyBroadException
                try:
                    os.remove(self._fullpath)
                    os.remove(new_path)
                except:
                    pass
                return dict(success=False, error=_("Error saving image"))
            self._filename = ".".join([f_name, self._save_format.lower()])
        return dict(success=True, fullpath=self._fullpath, path=self._upload_dir,
                    old_filename=filename, filename=self._filename)


def addon_uploader(request, filetype='file', **kwargs):
    uploader = AjaxUploader(filetype=filetype)
    result = uploader.handle_upload(request)
    if result['success']:
        if filetype is 'image':
            new = Pic()
            target = new.img
        else:
            new = Doc()
            target = new.doc
        new.content_type = ContentType.objects.get_for_id(int(kwargs['content_type']))
        new.object_id = int(kwargs['object_id'])
        new.description = result['old_filename']
        new.user = request.user
        new.created_date = now()
        target = result['path']
        fullpath = os.path.join(settings.MEDIA_ROOT,
                                target.field.upload_to, target.path)
        new.size = os.path.getsize(fullpath)
        new.save()
        # noinspection PyBroadException
        if filetype is 'image':
            try:
                pics_count = dict(pics_count=new.content_object.pics_count)
                result.update(pics_count)
            except:
                pass
        try:
            if filetype is 'image':
                html = render_to_string('upload/image_item.html', {'pic': new})
            else:
                html=render_to_string('upload/file_item.html', {'doc': new})
            addons = dict(html=html)
        except:
            addons = dict()
        result.update(addons)
    return ajax_answer(result)


def addon_image_uploader(request, **kwargs):
    return addon_uploader(request, filetype='image', **kwargs)


def like(request, content_type, object_id):
    # noinspection PyBroadException
    try:
        if not request.user.is_authenticated:
            raise AccessError
        mode = request.POST['mode']
        if mode not in ['like', 'dislike']:
            raise AccessError
        content_type = ContentType.objects.get_for_id(int(content_type))
        object_id = int(object_id)
        if content_type == ContentType.objects.get_for_model(get_user_model()):
            if object_id == request.user.pk:
                raise AccessError
        else:
            obj = content_type.get_object_for_this_type(pk=object_id)
            if obj.user == request.user:
                pass  #raise AccessError
        # noinspection PyBroadException
        try:
            thelike = Like.objects.get(user=request.user, content_type=content_type, object_id=object_id)
        except:
            thelike = Like(user=request.user, content_type=content_type, object_id=object_id)
            thelike.save()
        if mode == 'like':
            if thelike.status is not None:
                if thelike.status:
                    thelike.status = None
                    like_en = False
                else:
                    thelike.status = True
                    like_en = True
            else:
                thelike.status = True
                like_en = True
            dislike_en = False
        else:
            if thelike.status is not None:
                if not thelike.status:
                    thelike.status = None
                    dislike_en = False
                else:
                    thelike.status = False
                    dislike_en = True
            else:
                thelike.status = False
                dislike_en = True
            like_en = False
        thelike.save()
        karma = thelike.content_object.karma
        payload = dict(success=True, karma=karma, liked=like_en, disliked=dislike_en)
    except AccessError as aerr:
        payload = dict(success=False, error=_("Not allowed"))
    except:
        payload = dict(success=False)
    return ajax_answer_lazy(payload)


def delete_comment(request, object_id, depth):
    payload = dict(success=False)
    try:
        if not request.user.is_authenticated:
            raise AccessError
        comment = Nnmcomment.objects.get(pk=int(object_id))
        if comment.user == request.user or request.user.is_superuser:
            comment.status = STATUS_LOCKED
            comment.save()
            newcomment = copy.deepcopy(comment)
            newcomment.depth = depth
            html = render_to_string('comments/comment_one.html', {'comment': newcomment, 'user': request.user})
            payload = dict(success=True, html=html, object_comments=comment.content_object.comments)
        else:
            raise AccessError
    except AccessError as aerr:
        pass
    except:
        pass
    return ajax_answer_lazy(payload)


def avatar_set(request):
    u = request.user
    uploader = AjaxUploader(filetype='image', size_limit=4096000)
    result = uploader.handle_upload(request)
    if result['success']:
        # noinspection PyBroadException
        try:
            remove_thumbnails(u.img.path)
            remove_file(u.img.path)
        except:
            pass
        u.img.save(result['filename'], File(open(result['path'] + '/' + result['filename'], 'rb')))
        u.save()
        # noinspection PyBroadException
        try:
            addons = dict(html=render_to_string('user/avatar.html', {'object': u}))
        except:
            addons = dict()
        result.update(addons)
    return ajax_answer_lazy(result)


def avatar_delete(request):
    # noinspection PyBroadException
    try:
        remove_thumbnails(request.user.img.path)
        remove_file(request.user.img.path)
        request.user.img = ''
        request.user.save()
        payload = dict(success=True)
        # noinspection PyBroadException
        try:
            addons = dict(html=render_to_string('user/avatar.html', {'object': request.user}))
        except:
            addons = dict()
        payload.update(addons)
    except:
        payload = dict(success=False)
    return ajax_answer_lazy(payload)
