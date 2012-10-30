from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from nnmware.core.imgutil import remove_thumbnails, remove_file
from nnmware.core.models import Tag, Follow, JComment
from nnmware.core.abstract import MetaDate

class Video(MetaDate):

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    project_name = models.CharField(max_length=50, verbose_name=_(u'Project Name'), blank=True)
    project_url = models.URLField(max_length=255, verbose_name=_(u'Project URL'), blank=True)
    video_url = models.URLField(max_length=255, verbose_name=_(u'Video URL'))
    video_provider = models.CharField(max_length=150, verbose_name=_(u'Video Provider'), blank=True)
    description = models.TextField(verbose_name=_(u'Description'), blank=True)
    thumbnail = models.ImageField(upload_to="video/%Y/%b/%d", blank=True)
    login_required = models.BooleanField(verbose_name=_("Login required"), default=False, help_text=_("Enable this if users must login before access with this objects."))
    slug = models.SlugField(_("Slug"), max_length=255, blank=True)
    duration = models.PositiveIntegerField(null=True,blank=True,editable=False)
    viewcount = models.PositiveIntegerField(default=0, editable=False)
    liked = models.PositiveIntegerField(default=0, editable=False)
    embedcode = models.TextField(verbose_name=_(u'Embed code'), blank=True)
    publish = models.BooleanField(_("Published"), default=False)
    tags = models.ManyToManyField(Tag)
    users_viewed = models.ManyToManyField(User, related_name='view_this_video')
    comments = models.IntegerField(blank=True, default=0)


    class Meta:
        verbose_name = _("Video")
        verbose_name_plural = _("Videos")
        ordering = ("-created_date",)

    def __unicode__(self):
        return _("%s") % self.project_name

    def delete(self, *args, **kwargs):
        try:
            remove_thumbnails(self.thumbnail.path)
            remove_file(self.thumbnail.path)
        except :
            pass
        super(Video, self).delete(*args, **kwargs)

    def followers_count(self):
        ctype = ContentType.objects.get_for_model(self)
        return Follow.objects.filter(content_type=ctype,object_id=self.id).count()

    def followers(self):
        ctype = ContentType.objects.get_for_model(self)
        users = Follow.objects.filter(content_type=ctype,object_id=self.id).values_list('user',flat=True)
        return User.objects.filter(pk__in=users)

    @permalink
    def get_absolute_url(self):
        return "video_detail", (), {'slug': self.slug}

    def tags2(self):
        return self.tags.all()[:2]

    def users_commented(self):
        ctype = ContentType.objects.get_for_model(self)
        users = JComment.objects.filter(content_type=ctype,object_id=self.id).values_list('user',flat=True)
        return User.objects.filter(pk__in=users)
