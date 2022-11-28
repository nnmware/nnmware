# nnmware(c)2012-2020

from __future__ import unicode_literals

from django.utils.timesince import timesince
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.utils.timezone import now
from django.db import models
from django.db.models import Manager, Sum, Count
from django.conf import settings
from django.urls import reverse
from django.db.models.signals import post_save, post_delete
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import slugify
from django.dispatch import receiver

from nnmware.core.abstract import Pic, Doc, AbstractContent, AbstractImg, AbstractDate, AbstractNnmcomment, \
    AbstractIP
from nnmware.core.constants import CONTENT_CHOICES, CONTENT_UNKNOWN, STATUS_CHOICES, NOTICE_CHOICES, NOTICE_UNKNOWN, \
    STATUS_DRAFT, GENDER_CHOICES, ACTION_CHOICES, ACTION_UNKNOWN
from nnmware.core.utils import setting, send_template_mail
from nnmware.core.managers import AbstractContentManager, NnmcommentManager, FollowManager, MessageManager


class Tag(models.Model):
    """
    Model for Tags
    """
    name = models.CharField(_('Name'), max_length=40, unique=True, db_index=True)
    slug = models.SlugField(_("URL"), max_length=40, unique=True)
    follow = models.PositiveIntegerField(default=0, editable=False)

    objects = Manager()

    class Meta:
        ordering = ('name',)
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Tag, self).save(*args, **kwargs)

    def lettercount(self):
        return Tag.objects.filter(name__startswith=self.name[0]).count()

    def __str__(self):
        return self.name

    def followers_count(self):
        ctype = ContentType.objects.get_for_model(self)
        return Follow.objects.filter(content_type=ctype, object_id=self.pk).count()

    def followers(self):
        ctype = ContentType.objects.get_for_model(self)
        users = Follow.objects.filter(content_type=ctype, object_id=self.pk).values_list('user', flat=True)
        return get_user_model().objects.filter(pk__in=users)

    def get_absolute_url(self):
        return reverse('tag_detail', args=[self.slug])


class FlatNnmcomment(AbstractNnmcomment):
    pass

    objects = AbstractContentManager()


class Nnmcomment(AbstractNnmcomment):
    """
    A threaded comment
    """
    # Hierarchy Field
    parent = models.ForeignKey('self', null=True, blank=True, default=None, related_name='children',
                               on_delete=models.CASCADE)

    objects = NnmcommentManager()

    class Meta:
        ordering = ('-created_date',)
        verbose_name = _("Threaded Comment")
        verbose_name_plural = _("Threaded Comments")
        get_latest_by = "created_date"


class Follow(AbstractContent):
    """
    Lets a user follow the activities of any specific actor
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Follow'), null=True, blank=True,
                             related_name='follow', on_delete=models.CASCADE)

    objects = FollowManager()

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')
        verbose_name = _("Follow")
        verbose_name_plural = _("Follows")

    def __str__(self):
        return '%s -> %s' % (self.user, self.content_object)


class Notice(AbstractContent, AbstractIP):
    """
    User notification model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notice_type = models.IntegerField(_("Notice Type"), choices=NOTICE_CHOICES, default=NOTICE_UNKNOWN)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='notice_sender', on_delete=models.CASCADE)
    verb = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=now)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _("Notice")
        verbose_name_plural = _("Notices")


class Message(AbstractIP):
    """
    A private message from user to user
    """
    subject = models.CharField(_("Subject"), max_length=120, blank=True)
    body = models.TextField(_("Body"))
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sender_messages',
                               verbose_name=_("Sender"), on_delete=models.CASCADE)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='receiver_messages', null=True,
                                  blank=True, verbose_name=_("Recipient"), on_delete=models.CASCADE)
    parent_msg = models.ForeignKey('self', related_name='next_messages', null=True, blank=True,
                                   verbose_name=_("Parent message"), on_delete=models.CASCADE)
    sent_at = models.DateTimeField(_("sent at"), null=True, blank=True)
    read_at = models.DateTimeField(_("read at"), null=True, blank=True)
    replied_at = models.DateTimeField(_("replied at"), null=True, blank=True)
    sender_deleted_at = models.DateTimeField(_("Sender deleted at"), null=True, blank=True)
    recipient_deleted_at = models.DateTimeField(_("Recipient deleted at"), null=True, blank=True)
    objects = MessageManager()

    def new(self):
        """returns whether the recipient has read the message or not"""
        if self.read_at is not None:
            return False
        return True

    def replied(self):
        """returns whether the recipient has written a reply to this message"""
        if self.replied_at is not None:
            return True
        return False

    def __str__(self):
        if self.subject is not None:
            return self.subject
        if self.body is not None:
            return self.body[:40]
        return None

    def get_absolute_url(self):
        return reverse('messages_detail', args=[self.id])

    def save(self, **kwargs):
        if not self.id:
            self.sent_at = now()
        super(Message, self).save(**kwargs)

    class Meta:
        ordering = ['-sent_at']
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")


class Action(AbstractContent, AbstractIP):
    """
    Model Activity of User
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='actions', on_delete=models.CASCADE)
    action_type = models.IntegerField(_("Action Type"), choices=ACTION_CHOICES, default=ACTION_UNKNOWN)
    verb = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=now)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _("Action")
        verbose_name_plural = _("Actions")

    @property
    def target_type(self):
        return ContentType.objects.get_for_model(self.content_object).model

    def __str__(self):
        return '%s %s %s ago' % (self.user, self.verb, self.time_since())

    def time_since(self, dt_now=None):
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the
        current timestamp.
        """
        return timesince(self.timestamp, dt_now)

    def get_absolute_url(self):
        return reverse('nnmware.core.views.detail', args=[self.pk])


@receiver([post_save, post_delete], sender=Nnmcomment)
def update_comment_count(sender, instance, **kwargs):
    # noinspection PyBroadException
    try:
        what = instance.get_content_object()
        what.comments = Nnmcomment.public.all_for_object(what).count()
        what.updated_date = now()
        what.save()
    except:
        pass


@receiver([post_save, post_delete], sender=FlatNnmcomment)
def update_post_date(sender, instance, **kwargs):
    # noinspection PyBroadException
    try:
        what = instance.get_content_object()
        what.comments = FlatNnmcomment.public.all_for_object(what).count()
        what.updated_date = now()
        what.save()
    except:
        pass


def update_pic_count(sender, instance, **kwargs):
    what = instance.get_content_object()
    what.pics = Pic.objects.for_object(what).count()
    what.save()


def update_doc_count(sender, instance, **kwargs):
    what = instance.get_content_object()
    what.docs = Doc.objects.for_object(what).count()
    what.save()


class VisitorHit(AbstractIP):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), blank=True,
                             null=True, on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name=_("Creation date"), default=now, db_index=True)
    session_key = models.CharField(max_length=40, verbose_name=_('Session key'), db_index=True)
    hostname = models.CharField(max_length=100, verbose_name=_('Hostname'), db_index=True)
    referer = models.TextField(verbose_name=_('Referer'))
    url = models.CharField(max_length=255, verbose_name=_('URL'), db_index=True)
    secure = models.BooleanField(_('Is secure'), default=False, db_index=True)

    class Meta:
        ordering = ['-date']
        verbose_name = _("Visitor hit")
        verbose_name_plural = _("Visitors hits")


class EmailValidationManager(Manager):
    """
    Email validation manager
    """
    def verify_for_confirm_email(self, key):
        """
        User and key verification on email confirmation
        return: user or None
        """
        try:
            verify = self.get(key=key)
        except self.model.DoesNotExist:
            return None
        user = verify.user
        if not user.is_active or user.is_confirmed:
            verify.delete()
            return None
        if not verify.is_expired():
            user.is_confirmed = True
            user.save()
            verify.delete()
            return user
        else:
            verify.delete()
            return None

    def verify_for_recovery_password(self, key):
        """
        User and key verification for password recovery
        return: EmailValidation or None
        """
        try:
            verify = self.get(key=key)
        except self.model.DoesNotExist:
            return None
        user = verify.user
        if not user.is_active or not user.is_confirmed:
            verify.delete()
            return None
        if not verify.is_expired():
            return verify
        else:
            verify.delete()
            return None

    @staticmethod
    def _send_validation_mail(key, user):
        template_body = "email/validation.txt"
        template_subject = "email/validation_subject.txt"
        mail_dict = {'key': key,
                     'site_name': Site.objects.get_current().name,
                     'domain': Site.objects.get_current().domain,
                     'username': user.username}
        send_template_mail(template_subject, template_body, mail_dict, [user.email])

    def add(self, user, send=True):
        """
        Add a new validation process entry
        """
        while True:
            key = get_user_model().objects.make_random_password(70)
            try:
                EmailValidation.objects.get(key=key)
            except self.model.DoesNotExist:
                self.key = key
                break

        if setting('REQUIRE_EMAIL_CONFIRMATION', True) and send:
            self._send_validation_mail(key, user)
        self.filter(user=user).delete()
        return self.create(user=user, key=key)

    def resend(self, user):
        """
        Resend validation email
        """
        e = getattr(user, 'emailvalidation', False)
        if e and not e.is_expired():
            self._send_validation_mail(e.key, e.user)
        else:
            self.add(user)

    def recover_password(self, user):
        e = self.add(user, send=False)
        e.password = get_user_model().objects.make_random_password(30)
        e.save()
        template_body = "email/changepass.txt"
        template_subject = "email/changepass_subject.txt"
        mail_dict = {'key': e.key,
                     'site_name': Site.objects.get_current().name,
                     'domain': Site.objects.get_current().domain,
                     'email': user.email,
                     'username': user.username}
        send_template_mail(template_subject, template_body, mail_dict, [user.email])


class EmailValidation(models.Model):
    """
    Email Validation model
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_('User'), on_delete=models.CASCADE)
    password = models.CharField(max_length=30, default='')
    key = models.CharField(verbose_name=_('Validation key'), max_length=70, unique=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = EmailValidationManager()

    class Meta:
        ordering = ['user', '-created']
        verbose_name = _("Email Validation")
        verbose_name_plural = _("Email Validations")

    def __str__(self):
        return f'{_("Email validation process for")} {self.user}'

    def is_expired(self):
        return (now() - self.created).days > setting('EMAIL_VALIDATION_DAYS', 1)


class Video(AbstractDate, AbstractImg):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project_name = models.CharField(max_length=50, verbose_name=_('Project Name'), blank=True)
    project_url = models.URLField(max_length=255, verbose_name=_('Project URL'), blank=True)
    video_url = models.URLField(max_length=255, verbose_name=_('Video URL'))
    video_provider = models.CharField(max_length=150, verbose_name=_('Video Provider'), blank=True)
    description = models.TextField(verbose_name=_('Description'), blank=True)
    login_required = models.BooleanField(verbose_name=_("Login required"), default=False, help_text=_(
        "Enable this if users must login before access with this objects."))
    slug = models.SlugField(_("Slug"), max_length=255, blank=True)
    duration = models.PositiveIntegerField(null=True, blank=True, editable=False)
    viewcount = models.PositiveIntegerField(default=0, editable=False)
    liked = models.PositiveIntegerField(default=0, editable=False)
    embedcode = models.TextField(verbose_name=_('Embed code'), blank=True)
    publish = models.BooleanField(_("Published"), default=False)
    tags = models.ManyToManyField(Tag)
    users_viewed = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='view_this_video')
    comments = models.IntegerField(blank=True, default=0)

    class Meta:
        verbose_name = _("Video")
        verbose_name_plural = _("Videos")
        ordering = ("-created_date",)

    def __str__(self):
        return _("%s") % self.project_name

    def followers_count(self):
        ctype = ContentType.objects.get_for_model(self)
        return Follow.objects.filter(content_type=ctype, object_id=self.id).count()

    def followers(self):
        ctype = ContentType.objects.get_for_model(self)
        users = Follow.objects.filter(content_type=ctype, object_id=self.id).values_list('user', flat=True)
        return get_user_model().objects.filter(pk__in=users)

    def get_absolute_url(self):
        return reverse('video_detail', kwargs={'slug': self.slug})

    def tags2(self):
        return self.tags.all()[:2]

    def users_commented(self):
        ctype = ContentType.objects.get_for_model(self)
        users = Nnmcomment.objects.filter(content_type=ctype, object_id=self.id).values_list('user', flat=True)
        return get_user_model().objects.filter(pk__in=users)


class NnmwareUser(AbstractUser, AbstractImg):
    fullname = models.CharField(max_length=100, verbose_name=_('Full Name'), blank=True)
    birthdate = models.DateField(verbose_name=_('Date birth'), blank=True, null=True)
    gender = models.CharField(verbose_name=_("Gender"), max_length=1, choices=GENDER_CHOICES, blank=True)
    about = models.TextField(verbose_name=_('About'), help_text=_('Little words about you'), blank=True)
    date_modified = models.DateTimeField(default=now, editable=False)
    website = models.URLField(max_length=150, verbose_name=_('Website'), blank=True)
    facebook = models.URLField(max_length=150, verbose_name=_('Facebook'), blank=True)
    googleplus = models.URLField(max_length=150, verbose_name=_('Google+'), blank=True)
    twitter = models.URLField(max_length=150, verbose_name=_('Twitter'), blank=True)
    location = models.CharField(max_length=100, verbose_name=_('Location'), blank=True)
    icq = models.CharField(max_length=30, verbose_name=_('ICQ'), blank=True)
    skype = models.CharField(max_length=100, verbose_name=_('skype'), blank=True)
    jabber = models.CharField(max_length=100, verbose_name=_('jabber'), blank=True)
    telegram = models.CharField(max_length=100, verbose_name=_('telegram'), blank=True)
    mobile = models.CharField(max_length=100, verbose_name=_('mobile phone'), blank=True)
    workphone = models.CharField(max_length=100, verbose_name=_('work phone'), blank=True)
    publicmail = models.EmailField(verbose_name=_('Public email'), blank=True)
    signature = models.CharField(max_length=100, verbose_name=_('Signature'), blank=True)
    show_signatures = models.BooleanField(verbose_name=_('Show signatures'), blank=True, default=False)
    post_count = models.IntegerField(verbose_name=_('Post count'), blank=True, default=0)
    subscribe = models.BooleanField(verbose_name=_('Subscribe for news and updates'), default=False)
    balance = models.DecimalField(verbose_name=_('Balance'), default=0, max_digits=20, decimal_places=3)
    timezone = models.CharField(max_length=50, default='Europe/Moscow')
    is_confirmed = models.BooleanField(verbose_name=_("User is confirmed"), default=False)

    class Meta:
        ordering = ['username', ]
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        abstract = True

    def get_absolute_url(self):
        return reverse("user_detail", args=[self.username])

    def __str__(self):
        return "%s" % self.username

    @property
    def get_name(self):
        if self.fullname:
            return self.fullname
        else:
            return self.username

    def _ctype(self):
        return ContentType.objects.get_for_model(get_user_model())

    def followers_count(self):
        return Follow.objects.filter(content_type=self._ctype(), object_id=self.user.pk).count()

    def followers(self):
        users = Follow.objects.filter(content_type=self._ctype(), object_id=self.user.pk).values_list('user', flat=True)
        return get_user_model().objects.filter(pk__in=users)

    def follow_tags_count(self):
        ctype = ContentType.objects.get_for_model(Tag)
        return self.user.follow_set.filter(content_type=ctype).count()

    def follow_tags(self):
        ctype = ContentType.objects.get_for_model(Tag)
        tags_ids = self.user.follow_set.filter(content_type=ctype).values_list('object_id', flat=True)
        return map(lambda x: int(x), tags_ids)

    def loved_video_count(self):
        ctype = ContentType.objects.get_for_model(Video)
        return self.user.follow_set.filter(content_type=ctype).count()

    def follow_count(self):
        return self.user.follow_set.filter(content_type=self._ctype()).count()

    def basket_sum(self):
        from nnmware.apps.market.models import Basket
        all_sum = Basket.objects.filter(user=self).aggregate(Sum('sum'))
        return "%0.2f" % (all_sum,)

    @property
    def unread_msg_count(self):
        result = Message.objects.unread(self).count()
        if result > 0:
            return result
        return None

    def save(self, *args, **kwargs):
        self.date_modified = now()
        super(NnmwareUser, self).save(*args, **kwargs)

    @property
    def messages_count(self):
        return Message.objects.messages(self).count()


class Like(AbstractContent):
    """
    status = True or False or null
    """
    status = models.BooleanField(verbose_name="Status", null=True, default=None, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Author', blank=True,
                             null=True, on_delete=models.DO_NOTHING)

    class Meta:
        ordering = ('-pk',)
        verbose_name = "Like"
        verbose_name_plural = "Likes"

    def __str__(self):
        return 'Likes for %s' % self.content_object


@receiver([post_save, post_delete], sender=Like)
def update_karma(sender, instance, **kwargs):
    what = instance.get_content_object()
    # noinspection PyBroadException
    try:
        what.set_karma()
    except:
        pass


class LikeMixin(models.Model):
    karma = models.IntegerField(verbose_name=_("Karma"), default=0, db_index=True)

    class Meta:
        abstract = True

    def set_karma(self):
        liked = Like.objects.for_object(self).filter(user__is_active=True, status=True).\
            aggregate(Count("id"))['id__count']
        disliked = Like.objects.for_object(self).filter(user__is_active=True, status=False).\
            aggregate(Count("id"))['id__count']
        self.karma = liked - disliked
        self.save()

    def users_liked(self):
        return Like.objects.for_object(self).filter(user__is_active=True, status=True).\
            values_list('user__pk', flat=True)

    def users_disliked(self):
        return Like.objects.for_object(self).filter(user__is_active=True, status=False).\
            values_list('user__pk', flat=True)


class ContentBlock(AbstractContent, AbstractIP, AbstractDate, AbstractImg):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), null=True, blank=True,
                             related_name="%(app_label)s_%(class)s_user", on_delete=models.SET_NULL)
    position = models.PositiveSmallIntegerField(verbose_name=_('Priority'), db_index=True, default=0,
                                                blank=True)
    status = models.IntegerField(_("Status"), choices=STATUS_CHOICES, default=STATUS_DRAFT)
    content_style = models.IntegerField(_("Content style"), choices=CONTENT_CHOICES, default=CONTENT_UNKNOWN)
    description = models.TextField(verbose_name=_('Content'), blank=True, default='')
    url = models.URLField(verbose_name=_('Origin url'), max_length=255, blank=True, default='')
    author = models.CharField(max_length=255, verbose_name=_('Author'), blank=True, default='')
    teaser = models.BooleanField(verbose_name=_('Block in teaser?'), default=False)

    class Meta:
        verbose_name = _("Content block")
        verbose_name_plural = _("Content blocks")
        ordering = ("-created_date",)
        get_latest_by = "created_date"

    def __str__(self):
        if len(self.description) > 50:
            return self.description[:50] + "..."
        return str(self.pk)


class ContentBlockMixin(object):

    @property
    def blocks(self):
        return ContentBlock.objects.for_object(self).order_by('position')

    @property
    def teasers(self):
        return self.blocks.filter(teaser=True)

    def delete(self, *args, **kwargs):
        self.blocks.delete()
        super(ContentBlockMixin, self).delete(*args, **kwargs)
