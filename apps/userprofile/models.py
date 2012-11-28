import datetime
from django.contrib.auth import get_user_model

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.template import loader, Context
from nnmware.apps.shop.models import Basket
from nnmware.core.models import Follow, Tag, Pic, Message

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


class Profile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, unique=True, related_name='user_profile')
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
    avatar = models.ForeignKey(Pic, blank=True, null=True)

    class Meta:
        ordering = ['user', ]
        verbose_name = _(" User Profile")
        verbose_name_plural = _("Users Profiles")

    def delete(self, *args, **kwargs):
        self.avatar.delete()
        super(Profile, self).delete(*args, **kwargs)

    def __unicode__(self):
        return _("%s's userprofile") % self.user

    @property
    def get_avatar(self):
        try: #if self.avatar:
            return self.avatar.pic.url
        except :
            return settings.DEFAULT_AVATAR

    @property
    def get_name(self):
        if self.fullname:
            return self.fullname
        else:
            return self.user.username

    def _ctype(self):
        return ContentType.objects.get_for_model(get_user_model())

    def followers_count(self):
        return Follow.objects.filter(content_type=self._ctype(),object_id=self.user.pk).count()

    def followers(self):
        users = Follow.objects.filter(content_type=self._ctype(),object_id=self.user.pk).values_list('user',flat=True)
        return get_user_model().objects.filter(pk__in=users)

    def follow_tags_count(self):
        ctype = ContentType.objects.get_for_model(Tag)
        return self.user.follow_set.filter(content_type=ctype).count()

    def follow_tags(self):
        ctype = ContentType.objects.get_for_model(Tag)
        tags_ids = self.user.follow_set.filter(content_type=ctype).values_list('object_id',flat=True)
        return map(lambda x: int(x), tags_ids)

    def follow_count(self):
        return self.user.follow_set.filter(content_type=self._ctype()).count()


    def get_absolute_url(self):
        return reverse("user_detail", args=[self.user.username])

    def basket_sum(self):
        basket_user = Basket.objects.filter(user=self.user)
        all_sum = 0
        for item in basket_user:
            all_sum += item.sum
        return "%0.2f" % (all_sum,)


    @property
    def unread_msg_count(self):
        result = Message.objects.unread(self.user).count()
        if result > 0:
            return result
        return None

    def save(self, *args, **kwargs):
        self.date_modified = datetime.datetime.now()
        super(Profile, self).save(*args, **kwargs)


#def create_user_profile(sender, instance, created, **kwargs):
#    if created:
#        Profile.objects.create(user=instance)
#
#post_save.connect(create_user_profile, sender=get_user_model())

