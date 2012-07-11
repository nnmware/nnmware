# -*- coding: utf-8 -*-
from datetime import timedelta
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from nnmware.apps.video.models import Video
from nnmware.apps.video.forms import VideoAddForm
from nnmware.core import oembed
from nnmware.core.backends import image_from_url
from nnmware.core.models import Tag, Follow
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
        return super(VideoAdd, self).form_valid(form)

class VideoDetail(DetailView):
    # For case-sensitive need UTF8_BIN collation in Slug_Field
    model = Video
    slug_field = 'slug'
    template_name = "video/detail.html"

    def get_context_data(self, **kwargs):
        context = super(VideoDetail, self).get_context_data(**kwargs)
        context['object'].embedcode = update_video_size(context['object'].embedcode,620,350)
        context['ctype'] = ContentType.objects.get_for_model(Video)
        self.object.viewcount += 1
        self.object.save()
        return context

class VideoTimelineFeed(ListView):
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
