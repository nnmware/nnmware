# -*- coding: utf-8 -*-
from datetime import timedelta
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from nnmware.apps.video.models import Video
from nnmware.apps.video.forms import VideoAddForm
from nnmware.core import oembed
from nnmware.core.backends import image_from_url
from nnmware.core.models import Tag, Follow, Action, JComment, ACTION_ADDED
from nnmware.core.signals import action
from nnmware.core.utils import gen_shortcut, get_oembed_end_point, get_video_provider_from_link
from nnmware.core.utils import update_video_size
from nnmware.core.views import AjaxFormMixin, TagDetail

class VideoAdd(AjaxFormMixin, FormView):
    model = Video
    form_class = VideoAddForm
    template_name = "video/add.html"
#    success_url = "/_video"

    def form_valid(self, form):
        link = form.cleaned_data.get('video_url')
        if not link[:7] == 'http://':
            link = 'http://%s' % link
        if link.find(u'youtu.be') != -1:
            link = link.replace('youtu.be/','www.youtube.com/watch?v=')
        consumer = oembed.OEmbedConsumer()
        # TODO: more code security here - big chance to get fatal error
        endpoint = get_oembed_end_point(link)
        #
        consumer.addEndpoint(endpoint)
        response = consumer.embed(link)
        result = response.getData()
        obj = Video()
        obj.embedcode = result['html']
        obj.thumbnail = image_from_url(result['thumbnail_url'])
        if result.has_key('duration'):
            obj.duration = result['duration']
        obj.user = self.request.user
        obj.project_name = form.cleaned_data.get('project_name')
        obj.project_url = form.cleaned_data.get('project_url')
        obj.video_provider = get_video_provider_from_link(form.cleaned_data.get('video_url'))
        obj.publish = True
        obj.description = form.cleaned_data.get('description')
        obj.video_url = link
        obj.save()
        obj.slug = gen_shortcut(obj.id)
        tags = form.cleaned_data.get('tags')
        alltags = Tag.objects.all().filter(name__in=tags)
        for tag in tags:
            obj.tags.add(alltags.get(name=tag))
            obj.save()
        self.success_url = obj.get_absolute_url()
        action.send(self.request.user, verb=_('added the video'), action_type=ACTION_ADDED, target=obj)
        return super(VideoAdd, self).form_valid(form)

class VideoDetail(SingleObjectMixin, ListView):
    # For case-sensitive need UTF8_BIN collation in Slug_Field
    paginate_by = 20
    template_name = "video/detail.html"

    def get_object(self, queryset=None):
        return get_object_or_404(Video, slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        kwargs['object'] = self.object
        context = super(VideoDetail, self).get_context_data(**kwargs)
        context['object'].embedcode = update_video_size(context['object'].embedcode,640,363)
        context['ctype'] = ContentType.objects.get_for_model(Video)
        self.object.viewcount += 1
        if self.request.user.is_authenticated():
            if self.request.user not in self.object.users_viewed.all():
                self.object.users_viewed.add(self.request.user)
        self.object.save()
        return context

    def get_queryset(self):
        self.object = self.get_object()
        return JComment.public.get_tree(self.object)

class VideoTimelineFeed(ListView):
    paginate_by = 5
    model = Video
    template_name = "video/timeline.html"

    def get_queryset(self):
        ctype = ContentType.objects.get_for_model(Tag)
        tags_id = Follow.objects.filter(user=self.request.user,content_type=ctype).values_list('object_id',flat=True)
        tags = Tag.objects.filter(pk__in=tags_id)
        return Video.objects.filter(tags__in=tags).order_by('-publish_date').distinct()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(VideoTimelineFeed, self).get_context_data(**kwargs)
        context['tab'] = 'timeline'
        context['tab_message'] = 'TODAY:'
        return context


class VideoPopularFeed(ListView):
    paginate_by = 12
    model = Video
    template_name = "video/feed.html"

    def get_queryset(self):
        return Video.objects.filter(publish_date__gte=datetime.now()-timedelta(days=1)).order_by('-viewcount')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(VideoPopularFeed, self).get_context_data(**kwargs)
        context['tab'] = 'popular'
        context['tab_message'] = 'POPULAR AT 24 HOURS AND MAX VIEWS:'
        return context


class VideoLatestFeed(ListView):
    model = Video
    paginate_by = 12
    template_name = "video/feed.html"

    def get_queryset(self):
        return Video.objects.order_by('-publish_date')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(VideoLatestFeed, self).get_context_data(**kwargs)
        context['tab'] = 'latest'
        context['tab_message'] = 'ALL LATEST VIDEOS:'
        return context


class VideoLovedFeed(ListView):
    paginate_by = 12
    model = Video
    template_name = "video/feed.html"

    def get_queryset(self):
        return Video.objects.filter(publish_date__gte=datetime.now()-timedelta(days=1)).order_by('-viewcount')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(VideoLovedFeed, self).get_context_data(**kwargs)
        context['tab'] = 'loved'
        context['tab_message'] = 'LOVED ON 24 HOURS:'
        return context

class TagSubscribers(TagDetail):
    template_name = "tag/subscribers.html"

    def get_context_data(self, **kwargs):
        context = super(TagSubscribers, self).get_context_data(**kwargs)
        context['tab'] = 'subscribers'
        return context

class UserPathMixin(object):

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        kwargs['object'] = self.object
        return super(UserPathMixin, self).get_context_data(**kwargs)

class UserActivity(UserPathMixin, SingleObjectMixin, ListView):
    paginate_by = 20
    template_name = "user/activity.html"

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(UserActivity, self).get_context_data(**kwargs)
        #        ctype = ContentType.objects.get_for_model(User)
        context['actions_list'] = Action.objects.filter(user=self.object) #actor_content_type=ctype, actor_object_id=self.object.id)
        context['tab'] = 'activity'
        context['tab_message'] = 'THIS USER ACTIVITY:'
        return context

    def get_queryset(self):
        self.object = self.get_object()
        return Action.objects.filter(user=self.object)


class UserVideoAdded(UserPathMixin, SingleObjectMixin, ListView):
    paginate_by = 12
    template_name = "user/added_video.html"

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(UserVideoAdded, self).get_context_data(**kwargs)
        context['added'] = Video.objects.filter(user=self.object).count()
        context['ctype'] = ContentType.objects.get_for_model(User)
        context['tab'] = 'added'
        context['tab_message'] = 'VIDEO ADDED THIS USER:'
        return context

    def get_queryset(self):
        self.object = self.get_object()
        return Video.objects.filter(user=self.object).order_by('-publish_date')

class UserVideoLoved(UserPathMixin, SingleObjectMixin, ListView):
    paginate_by = 12
    template_name = "user/loved_video.html"

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(UserVideoLoved, self).get_context_data(**kwargs)
        context['added'] = Video.objects.filter(user=self.object).count()
        context['ctype'] = ContentType.objects.get_for_model(User)
        context['tab'] = 'loved'
        context['tab_message'] = 'LOVED VIDEOS:'
        return context

    def get_queryset(self):
        self.object = self.get_object()
        follow = self.object.follow_set.filter(content_type=ContentType.objects.get_for_model(Video)).values_list('object_id',flat=True)
        return Video.objects.filter(id__in=follow)


class UserFollowTags(UserPathMixin, SingleObjectMixin, ListView):
    paginate_by = 20
    template_name = "user/follow_tags.html"

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(UserFollowTags, self).get_context_data(**kwargs)
        context['added'] = Video.objects.filter(user=self.object).count()
        context['ctype'] = ContentType.objects.get_for_model(User)
        context['tab'] = 'follow_tags'
        context['tab_message'] = 'USER FOLLOW THIS TAGS:'
        return context

    def get_queryset(self):
        self.object = self.get_object()
        follow = self.object.follow_set.filter(content_type=ContentType.objects.get_for_model(Tag)).values_list('object_id',flat=True)
        return Tag.objects.filter(id__in=follow)

class UserFollowUsers(UserPathMixin, SingleObjectMixin, ListView):
    paginate_by = 20
    template_name = "user/user_follow_list.html"

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(UserFollowUsers, self).get_context_data(**kwargs)
        context['added'] = Video.objects.filter(user=self.object).count()
        context['ctype'] = ContentType.objects.get_for_model(User)
        context['tab'] = 'follow_users'
        context['tab_message'] = 'USER FOLLOW THIS USERS:'
        return context

    def get_queryset(self):
        self.object = self.get_object()
        follow = self.object.follow_set.filter(content_type=ContentType.objects.get_for_model(User)).values_list('object_id',flat=True)
        return User.objects.filter(id__in=follow)

class UserFollowerUsers(UserPathMixin, SingleObjectMixin, ListView):
    paginate_by = 20
    template_name = "user/user_follow_list.html"

    def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
        context = super(UserFollowerUsers, self).get_context_data(**kwargs)
        context['added'] = Video.objects.filter(user=self.object).count()
        context['ctype'] = ContentType.objects.get_for_model(User)
        context['tab'] = 'follower_users'
        context['tab_message'] = 'USERS FOLLOW ON THIS USER:'
        return context

    def get_queryset(self):
        self.object = self.get_object()
        followers = Follow.objects.filter(object_id=self.object.id, content_type=ContentType.objects.get_for_model(User)).values_list('user',flat=True)
        return User.objects.filter(id__in=followers)
