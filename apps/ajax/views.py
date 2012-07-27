# -*- coding: utf-8 -*-
from datetime import datetime
import os
import Image
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import linebreaksbr
from nnmware.apps.userprofile.models import Profile
from nnmware.apps.video.models import Video
from nnmware.core.actions import follow, unfollow
from nnmware.core.ajax import AjaxFileUploader, AjaxImageUploader, AjaxAvatarUploader, AjaxAnswer
from django.utils.translation import ugettext_lazy as _
from nnmware.core.imgutil import remove_thumbnails, remove_file, make_thumbnail
from nnmware.core.models import Tag, Follow, Notice, Message, Pic, Doc, JComment
from nnmware.core import oembed
from nnmware.core.backends import image_from_url
from nnmware.core.signals import action, notice
from nnmware.core.utils import get_oembed_end_point, update_video_size
from nnmware.core.ajax import AjaxLazyAnswer
from nnmware.core.file import get_path_from_url

class AccessError(Exception):
    pass


def get_video(request):
    link = request.REQUEST['link']
    if not link[:7] == 'http://':
        link = 'http://%s' % link
    if link.find(u'youtu.be') != -1:
        link = link.replace('youtu.be/','www.youtube.com/watch?v=')
    try:
        search_qs = Video.objects.filter(video_url=link)[0]
    except:
        search_qs = False
    if search_qs:
        payload = {'success': False, 'location':search_qs.get_absolute_url()}
    else:  #try:
        consumer = oembed.OEmbedConsumer()
        endpoint = get_oembed_end_point(link)
        consumer.addEndpoint(endpoint)
        response = consumer.embed(link)
        result = response.getData()
        result['html'] = update_video_size(result['html'],500,280)
        payload = {'success': True, 'data': result}
#    except:
#        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def video_like(request, object_id):
    # Link used for User press Like on Video Detail Page
    object_id = object_id
    video = get_object_or_404(Video, id=int(object_id))
    ctype = ContentType.objects.get_for_model(Video)
    payload = {'success': False}
    if not Follow.objects.filter(user=request.user,content_type=ctype,object_id=object_id).count():
        if follow(request.user, video):
            action.send(request.user, verb=_('liked the video'), target=video)
            if request.user.get_profile().followers_count:
                for u in User.objects.filter(pk__in=request.user.get_profile().followers):
                    if u.follow_set.filter(content_type=ctype, object_id=video.pk).count:
                        notice.send(request.user, user=u, verb=_('also now liked'), target=video)
                    else:
                        notice.send(request.user, user=u, verb=_('now liked'), target=video)
            video.liked = Follow.objects.filter(content_type=ctype, object_id=object_id).count()
            video.save()
            result = video.liked
            payload = {'success': True, 'count': result}
    return AjaxLazyAnswer(payload)

def video_dislike(request, object_id):
    # Link used for User press Like on Video Detail Page
    object_id = object_id
    video = get_object_or_404(Video, id=int(object_id))
    ctype = ContentType.objects.get_for_model(Video)
    payload = {'success': False}
    if Follow.objects.filter(user=request.user,content_type=ctype,object_id=object_id).count():
        if unfollow(request.user, video):
            action.send(request.user, verb=_('disliked the video'), target=video)
            if request.user.get_profile().followers_count:
                for u in User.objects.filter(pk__in=request.user.get_profile().followers):
                    notice.send(request.user, user=u, verb=_('now disliked'), target=video)
            video.liked = Follow.objects.filter(content_type=ctype, object_id=object_id).count()
            video.save()
            result = video.liked
            payload = {'success': True, 'count': result}
    return AjaxLazyAnswer(payload)


def check_tag(request, object_id):
    object_id = object_id
    ctype = ContentType.objects.get_for_model(Tag)
    if not Follow.objects.filter(user=request.user,content_type=ctype,object_id=object_id).count():
        return follow_tag(request, object_id)
    else:
        return unfollow_tag(request, object_id)

def follow_tag(request, object_id):
    # Link used for User press Like on Video Detail Page
    object_id = object_id
    tag = get_object_or_404(Tag, id=int(object_id))
    ctype = ContentType.objects.get_for_model(Tag)
    if not Follow.objects.filter(user=request.user,content_type=ctype,object_id=object_id).count():
        follow(request.user, tag)
        action.send(request.user, verb=_('follow the tag'), target=tag)
        if request.user.get_profile().followers_count:
            for u in User.objects.filter(pk__in=request.user.get_profile().followers):
                if u.follow_set.filter(content_type=ctype, object_id=tag.pk).count:
                    notice.send(request.user, user=u, verb=_('also now follow'), target=tag)
                else:
                    notice.send(request.user, user=u, verb=_('now follow'), target=tag)
        tag.follow = Follow.objects.filter(content_type=ctype, object_id=object_id).count()
        tag.save()
        result = tag.follow
        payload = {'success': True, 'count': result}
    else:
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def unfollow_tag(request, object_id):
    # Link used for User press Like on Video Detail Page
    object_id = object_id
    tag = get_object_or_404(Tag, id=int(object_id))
    ctype = ContentType.objects.get_for_model(Tag)
    if Follow.objects.filter(user=request.user,content_type=ctype,object_id=object_id).count():
        unfollow(request.user, tag)
        action.send(request.user, verb=_('unfollow the tag'), target=tag)
        if request.user.get_profile().followers_count:
            for u in User.objects.filter(pk__in=request.user.get_profile().followers):
                notice.send(request.user, user=u, verb=_('now follow'), target=tag)
        tag.follow = Follow.objects.filter(content_type=ctype, object_id=object_id).count()
        tag.save()
        result = tag.follow
        payload = {'success': True, 'count': result}
    else:
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def check_notify(request):
    try:
        profile = request.user.get_profile()
        if profile.subscribe:
            profile.subscribe = False
        else:
            profile.subscribe = True
        profile.save()
        payload = {'success': True}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def check_user(request, object_id):
    object_id = object_id
    ctype = ContentType.objects.get_for_model(User)
    if not Follow.objects.filter(user=request.user,content_type=ctype,object_id=object_id).count():
        return follow_user(request, object_id)
    else:
        return unfollow_user(request, object_id)

def follow_user(request, object_id):
    # Link used for User press Follow on User Detail Page
    object_id = object_id
    user = get_object_or_404(User, id=int(object_id))
    ctype = ContentType.objects.get_for_model(User)
    if not Follow.objects.filter(user=request.user,content_type=ctype,object_id=object_id).count():
        follow(request.user, user)
        action.send(request.user, verb=_('follow the user'), target=user)
        if request.user.get_profile().followers_count:
            for u in User.objects.filter(pk__in=request.user.get_profile().followers):
                if u.follow_set.filter(content_type=ctype, object_id=user.pk).count:
                    notice.send(request.user, user=u, verb=_('also now follow'), target=user)
                else:
                    notice.send(request.user, user=u, verb=_('now follow'), target=user)
        user.get_profile().follow = Follow.objects.filter(content_type=ctype, object_id=object_id).count()
        user.get_profile().save()
        result = user.get_profile().follow
        payload = {'success': True, 'count': result, 'id': user.pk}
    else:
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def unfollow_user(request, object_id):
    # Link used for User press Unfollow on User Detail Page
    object_id = object_id
    user = get_object_or_404(User, id=int(object_id))
    ctype = ContentType.objects.get_for_model(User)
    if Follow.objects.filter(user=request.user,content_type=ctype,object_id=object_id).count():
        unfollow(request.user, user)
        action.send(request.user, verb=_('unfollow the user'), target=user)
        if request.user.get_profile().followers_count:
            for u in User.objects.filter(pk__in=request.user.get_profile().followers):
                notice.send(request.user, user=u, verb=_('now unfollow'), target=user)
        user.get_profile().follow = Follow.objects.filter(content_type=ctype, object_id=object_id).count()
        user.get_profile().save()
        result = user.get_profile().follow
        payload = {'success': True, 'count': result, 'id': user.pk}
    else:
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def push_user(request, object_id):
    # Link used for User press button in user panel
    if 1>0: #try:
        object_id = int(object_id)
        user = get_object_or_404(User, id=int(object_id))
        ctype = ContentType.objects.get_for_model(User)
        status = False
        if Follow.objects.filter(user=request.user,content_type=ctype,object_id=object_id).count():
            unfollow(request.user, user)
            action.send(request.user, verb=_('unfollow the user'), target=user)
            if request.user.get_profile().followers_count:
                for u in User.objects.filter(pk__in=request.user.get_profile().followers):
                    notice.send(request.user, user=u, verb=_('now unfollow'), target=user)
        else:
            follow(request.user, user)
            status = True
            action.send(request.user, verb=_('follow the user'), target=user)
            if request.user.get_profile().followers_count:
                for u in User.objects.filter(pk__in=request.user.get_profile().followers):
                    if u.follow_set.filter(content_type=ctype, object_id=user.pk).count:
                        notice.send(request.user, user=u, verb=_('also now follow'), target=user)
                    else:
                        notice.send(request.user, user=u, verb=_('now follow'), target=user)
        user.get_profile().follow = Follow.objects.filter(content_type=ctype, object_id=object_id).count()
        user.get_profile().save()
        result = user.get_profile().follow
        payload = {'success': True, 'count': result, 'id': user.pk, 'status':status}
#    except :
#        payload = {'success': False}
    return AjaxLazyAnswer(payload)


def follow_object(request, content_type_id, object_id):
    """
    Creates the follow relationship between ``request.user`` and the
    actor defined by ``content_type_id``, ``object_id``.
    """
    ctype = get_object_or_404(ContentType, id=content_type_id)
    if not Follow.objects.filter(user=request.user,content_type=ctype,object_id=object_id).count():
        actor = ctype.get_object_for_this_type(id=object_id)
        follow(request.user, actor)
        success = True
    else:
        success = False
    count = Follow.objects.filter(content_type=ctype,object_id=object_id).count()
    payload = {'success': success, 'count': count}
    return AjaxLazyAnswer(payload)

def unfollow_object(request, content_type_id, object_id):
    """
    Creates the follow relationship between ``request.user`` and the
    actor defined by ``content_type_id``, ``object_id``.
    """
    ctype = get_object_or_404(ContentType, id=content_type_id)
    if Follow.objects.filter(user=request.user,content_type=ctype,object_id=object_id).count():
        actor = ctype.get_object_for_this_type(id=object_id)
        unfollow(request.user, actor, send_action=True)
        success = True
    else:
        success = False
    count = Follow.objects.filter(content_type=ctype,object_id=object_id).count()
    payload = {'success': success, 'count': count}
    return AjaxLazyAnswer(payload)


def autocomplete_users(request):
    search_qs = User.objects.filter(username__icontains=request.REQUEST['q'])
    results = []
    for r in search_qs:
        userstring = {'name': r.username, 'fullname': r.get_profile().fullname }
        results.append(userstring)
    payload = {'userlist': results}
    return AjaxLazyAnswer(payload)


def autocomplete_tags(request):
    search_qs = Tag.objects.filter(name__icontains=request.REQUEST['q'])
    results = []
    for r in search_qs:
        results.append(r.name)
    payload = {'q': results}
    return AjaxLazyAnswer(payload)

doc_uploader = AjaxFileUploader()
pic_uploader = AjaxImageUploader()
avatar_uploader = AjaxAvatarUploader()



def notice_delete(request, object_id):
    # Link used when User delete the notification
    if Notice.objects.get(user=request.user,id=object_id):
        Notice.objects.get(user=request.user,id=object_id).delete()
        result = Notice.objects.filter(user=request.user).count()
        payload = {'success': True, 'count': result}
    else:
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def avatar_delete(request):
    try:
        profile = request.user.get_profile()
        remove_thumbnails(profile.avatar.url)
        remove_file(profile.avatar.url)
        profile.avatar = ''
        profile.save()
        payload = {'success': True}
    except:
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def message_add(request):
    """
    Message add ajax
    """
    recipients = request.REQUEST['recipients'].strip().split(',')
    recipients = filter(None, recipients)  # Remove empty values
    try:
        for u in recipients:
            user = User.objects.get(username=u)
            if user and (user != request.user):
                m = Message()
                m.recipient = user
                m.sent_at = datetime.now()
                m.sender = request.user
                m.body = request.REQUEST['body']
                m.save()
        success = True
    except :
        success = False
    location = reverse('user_messages')
    payload = {'success': success, 'location':location}
    return AjaxLazyAnswer(payload)

def message_user_add(request):
    user = get_object_or_404(User,username=request.REQUEST['user'])
    result = dict()
    result['fullname'] = user.get_profile().get_name()
    result['url'] = user.get_absolute_url()
    result['username'] = user.username
    result['id'] = user.pk
    if user.get_profile().avatar:
        result['avatar_url'] = user.get_profile().avatar.url
    else:
        result['avatar_url'] = '/m/generic_t30.jpg'
    payload = {'success': True, 'data': result}
    #    except:
    #        payload = {'success': False}
    return AjaxLazyAnswer(payload)


def pic_delete(request, object_id):
    # Link used for User press Delete for Image
    pic = get_object_or_404(Pic, id=int(object_id))
    try:
        pic.delete()
        payload = {'success': True}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def pic_setmain(request, object_id):
    # TODO check user rights!!
    # Link used for User press SetMain for Image
    try:
        pic = Pic.objects.get(id=int(object_id))
        all_pics =Pic.objects.metalinks_for_object(pic.content_object)
        all_pics.update(primary=False)
        pic.primary = True
        pic.save()
        payload = {'success': True}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)


def doc_delete(request, object_id):
    # Link used for User press Delete for Image
    doc = get_object_or_404(Doc, id=int(object_id))
    try:
        doc.delete()
        payload = {'success': True}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def pic_getcrop(request, object_id):
    # Link used for User want crop image
    pic = get_object_or_404(Pic, id=int(object_id))
    try:
        payload = {'success': True,
                   'src': make_thumbnail(pic.pic.url,width=settings.MAX_IMAGE_CROP_WIDTH),
                   'id':pic.pk}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

def AjaxGetThumbnail(request):
    img_pk = int(request.REQUEST['image_id'])
    pic = get_object_or_404(Pic, id=int(img_pk))
    width = request.REQUEST.get('width') or None
    height = request.REQUEST.get('height') or None
    if width:
        width = int(width)
    if height:
        height = int(height)
    try:
        payload = {'success': True,
                   'src': make_thumbnail(pic.pic.url,width=width,height=height),
                   'id':pic.pk}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)


def ajax_image_crop(request):
    # Crop image
    try:
        img_pk = request.REQUEST['crop_id']
        pic = get_object_or_404(Pic, id=int(img_pk))
        if not request.user.is_superuser:
            parent_object = pic.content_object.__class__.__name__
            if parent_object == 'Room':
                if not request.user in pic.content_object.hotel.admins.all():
                    raise AccessError
            elif parent_object == 'Hotel':
                if not request.user in pic.content_object.admins.all():
                    raise AccessError
        left = int(request.REQUEST['crop_x1'])
        right = int(request.REQUEST['crop_x2'])
        top = int(request.REQUEST['crop_y1'])
        bottom = int(request.REQUEST['crop_y2'])
        box = [left, top, right, bottom]
        img = get_path_from_url(pic.pic.url)
        im = Image.open(img)
        if im.size[0] > settings.MAX_IMAGE_CROP_WIDTH:
            aspect_c = float(im.size[0])/settings.MAX_IMAGE_CROP_WIDTH
            box = map(lambda x: int(x*aspect_c), box)
        im = im.crop(box)
        if im.mode not in ('L', 'RGB'):
            im = im.convert('RGB')
        im.save(img)
        pic.save()
        payload = {'success': True, 'id':pic.pk}
    except AccessError:
        payload = {'success': False, 'error':_('You are not allowed change this image')}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)



def comment_add(request, content_type, object_id, parent_id=None):
    """
    Its Ajax posted comments
    """
    try:
        if not request.user.is_authenticated():
            raise AccessError
        comment = JComment()
        comment.user = request.user
        comment.content_type = get_object_or_404(ContentType, id=int(content_type))
        comment.object_id = int(object_id)
        comment.comment = request.REQUEST['comment']
        if len(comment.comment) == 0:
            raise AccessError
        kwargs={'content_type': content_type, 'object_id': object_id}
        if parent_id is not None:
            comment.parent_id = int(parent_id)
        comment.save()
        avatar_id = False
        kwargs['parent_id'] = comment.pk
        reply_link = reverse("jcomment_parent_add", kwargs=kwargs)
        comment_text = linebreaksbr(comment.comment)
        comment_date = comment.publish_date.strftime(settings.COMMENT_DATE_FORMAT)
        try:
            avatar_id = comment.user.get_profile().avatar.pk
        except :
            pass
        payload = {'success': True, 'id':comment.pk, 'username':comment.user.get_profile().get_name,
                   'username_url':comment.user.get_profile().get_absolute_url(),
                   'comment':comment_text, 'avatar_id':avatar_id,
                   'comment_date': comment_date, 'reply_link':reply_link,
                   'object_comments':comment.content_object.comments }
    except AccessError:
        payload = {'success': False, 'error':_('You are not allowed for add comment')}
    except :
        payload = {'success': False}
    return AjaxLazyAnswer(payload)

