import datetime
from decimal import Decimal
import re
import random
import os

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib import admin
from django.conf import settings
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.template import loader, Context
from nnmware.apps.video.models import Video

from nnmware.core import uuid
from nnmware.core.imgutil import remove_file, remove_thumbnails
from nnmware.core.backends import upload_avatar_dir
from nnmware.core.models import Follow, Tag

AVATAR_SIZES = (128, 96, 64, 48, 32, 24, 16)

GENDER_CHOICES = (('F', _('Female')), ('M', _('Male')),)
ACTION_RECORD_TYPES = (('A', 'Activation'),
                       ('R', 'Password reset'),
                       ('E', 'Email change'),
                       ('C', 'Comment approve')
    )

TZ_CHOICES = [(float(x[0]), x[1]) for x in (
    (-12, '-12'), (-11, '-11'), (-10, '-10'), (-9.5, '-09.5'), (-9, '-09'),
    (-8.5, '-08.5'), (-8, '-08 PST'), (-7, '-07 MST'), (-6, '-06 CST'),
    (-5, '-05 EST'), (-4, '-04 AST'), (-3.5, '-03.5'), (-3, '-03 ADT'),
    (-2, '-02'), (-1, '-01'), (0, '00 GMT'), (1, '+01 CET'), (2, '+02'),
    (3, '+03'), (3.5, '+03.5'), (4, '+04'), (4.5, '+04.5'), (5, '+05'),
    (5.5, '+05.5'), (6, '+06'), (6.5, '+06.5'), (7, '+07'), (8, '+08'),
    (9, '+09'), (9.5, '+09.5'), (10, '+10'), (10.5, '+10.5'), (11, '+11'),
    (11.5, '+11.5'), (12, '+12'), (13, '+13'), (14, '+14'),
    )]


def get_file_path(instance, filename):
    """
    This function generate filename with uuid4
    it's useful if:
    - you don't want to allow others to see original uploaded filenames
    - users can upload images with unicode in filenames wich
    can confuse browsers and fs
    """
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('pybb/avatar', filename)


class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)

    fullname = models.CharField(max_length=100, verbose_name=_(u'Full Name'), blank=True)
    birthdate = models.DateField(verbose_name=_(u'Date birth'), blank=True, null=True)
    gender = models.CharField(_("Gender"), max_length=1, choices=GENDER_CHOICES, blank=True)
    about = models.TextField(verbose_name=_(u'About'), help_text=_(u'Little words about you'), blank=True)
    date_modified = models.DateTimeField(default=datetime.datetime.now, editable=False)
    website = models.URLField(max_length=150, verbose_name=_(u'Website'), blank=True)
    facebook = models.URLField(max_length=150, verbose_name=_(u'Facebook'), blank=True)
    googleplus = models.URLField(max_length=150, verbose_name=_(u'Google+'), blank=True)
    twitter = models.URLField(max_length=150, verbose_name=_(u'Twitter'), blank=True)
    location = models.CharField(max_length=100, verbose_name=_(u'Location'), blank=True)
    icq = models.CharField(max_length=30, verbose_name=_(u'ICQ'), blank=True)
    skype = models.CharField(max_length=100, verbose_name=_(u'skype'), blank=True)
    jabber = models.CharField(max_length=100, verbose_name=_(u'jabber'), blank=True)
    mobile = models.CharField(max_length=100, verbose_name=_(u'mobile phone'), blank=True)
    workphone = models.CharField(max_length=100, verbose_name=_(u'work phone'), blank=True)
    publicmail = models.EmailField(_('Public email'), blank=True)
    signature = models.CharField(max_length=100, verbose_name=_('Signature'), blank=True)
    time_zone = models.FloatField(_('Time zone'), choices=TZ_CHOICES, default=float(settings.PROFILE_DEFAULT_TIME_ZONE), null=True,
        blank=True)
    show_signatures = models.BooleanField(_('Show signatures'), blank=True, default=False)
    post_count = models.IntegerField(_('Post count'), blank=True, default=0)
    subscribe = models.BooleanField(_('Subscribe for news and updates'), default=False)
    avatar = models.ImageField(upload_to=upload_avatar_dir, blank=True, null=True)
    avatar_complete = models.BooleanField(_('Avatar is set'), default=False, editable=False)


    class Meta:
        ordering = ['user', ]
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def delete(self, *args, **kwargs):
        try:
            remove_thumbnails(self.avatar.path)
            remove_file(self.avatar.path)
        except:
            pass
        super(Profile, self).delete(*args, **kwargs)

    def __unicode__(self):
        return _("%s's account") % self.user

    def get_name(self):
        if self.fullname:
            return self.fullname
        else:
            return self.user.username

    def followers_count(self):
        ctype = ContentType.objects.get_for_model(User)
        return Follow.objects.filter(content_type=ctype,object_id=self.user.id).count()

    def followers(self):
        ctype = ContentType.objects.get_for_model(User)
        return Follow.objects.filter(content_type=ctype,object_id=self.user.id).values_list('user',flat=True)

    def follow_tags_count(self):
        ctype = ContentType.objects.get_for_model(Tag)
        return self.user.follow_set.filter(content_type=ctype).count()

    def follow_tags(self):
        ctype = ContentType.objects.get_for_model(Tag)
        tags_ids = self.user.follow_set.filter(content_type=ctype).values_list('object_id',flat=True)
        return map(lambda x: int(x), tags_ids)

    def loved_video_count(self):
        ctype = ContentType.objects.get_for_model(Video)
        return self.user.follow_set.filter(content_type=ctype).count()

    def follow_count(self):
        ctype = ContentType.objects.get_for_model(User)
        return self.user.follow_set.filter(content_type=ctype).count()



    def get_absolute_url(self):
        return reverse("user_detail", args=[self.user.username])

    def save(self, *args, **kwargs):
        self.date_modified = datetime.datetime.now()
        super(Profile, self).save(*args, **kwargs)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

class EmailValidationManager(models.Manager):
    """
    Email validation manager
    """

    def verify(self, key):
        try:
            verify = self.get(key=key)
            if not verify.is_expired():
                verify.user.email = verify.email
                verify.user.is_active = True
                verify.user.save()
                verify.delete()
                return True
            else:
                verify.delete()
                return False
        except:
            return False

    def getuser(self, key):
        try:
            return self.get(key=key).user
        except:
            return False

    def add(self, user, email):
        """
        Add a new validation process entry
        """
        while True:
            key = User.objects.make_random_password(70)
            try:
                EmailValidation.objects.get(key=key)
            except EmailValidation.DoesNotExist:
                self.key = key
                break

        if settings.REQUIRE_EMAIL_CONFIRMATION:
            template_body = "account/email/validation.txt"
            template_subject = "account/email/validation_subject.txt"
            site_name, domain = Site.objects.get_current().name, \
                                Site.objects.get_current().domain
            body = loader.get_template(template_body).render(Context(locals()))
            subject = loader.get_template(template_subject)
            subject = subject.render(Context(locals())).strip()
            send_mail(subject=subject, message=body, from_email=None,
                recipient_list=[email])
            user = User.objects.get(username=str(user))
            self.filter(user=user).delete()
        return self.create(user=user, key=key, email=email)


class EmailValidation(models.Model):
    """
    Email Validation model
    """
    user = models.ForeignKey(User, unique=True)
    email = models.EmailField(blank=True)
    key = models.CharField(max_length=70, unique=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    objects = EmailValidationManager()

    class Meta:
        ordering = ['user', 'created']
        verbose_name = _("Email Validation")
        verbose_name_plural = _("Email Validations")

    def __unicode__(self):
        return _("Email validation process for %(user)s") % {'user': self.user}

    def is_expired(self):
        return (datetime.datetime.today() - self.created).days > 0

    def resend(self):
        """
        Resend validation email
        """
        template_body = "account/email/validation.txt"
        template_subject = "account/email/validation_subject.txt"
        site_name, domain = Site.objects.get_current().name, Site.objects.get_current().domain
        key = self.key
        body = loader.get_template(template_body).render(Context(locals()))
        subject = loader.get_template(template_subject)
        subject = subject.render(Context(locals())).strip()
        try:
            send_mail(subject=subject, message=body, from_email=None, recipient_list=[self.email])
        except:
            pass
        self.created = datetime.datetime.now()
        self.save()
        return True
