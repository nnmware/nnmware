# -*- coding: utf-8 -*-

"""
Base model library.
"""
from StringIO import StringIO
from datetime import datetime
import os
import Image
from django.contrib.auth.models import User
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import permalink, signals, Manager
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify, truncatewords_html
from django.utils.translation import get_language
from nnmware.core.managers import MetaLinkManager, JCommentManager, PublicJCommentManager, \
    FollowManager, MessageManager
from nnmware.core.imgutil import remove_thumbnails, remove_file
from nnmware.core.file import get_path_from_url

DEFAULT_MAX_JCOMMENT_LENGTH = getattr(settings, 'DEFAULT_MAX_JCOMMENT_LENGTH', 1000)
DEFAULT_MAX_JCOMMENT_DEPTH = getattr(settings, 'DEFAULT_MAX_JCOMMENT_DEPTH', 8)

STATUS_DELETE = 0
STATUS_LOCKED = 1
STATUS_PUBLISHED = 2
STATUS_STICKY = 3
STATUS_MODERATION = 4

STATUS_CHOICES = (
    (STATUS_DELETE, _("Deleted")),
    (STATUS_LOCKED, _("Locked")),
    (STATUS_PUBLISHED, _("Published")),
    (STATUS_STICKY, _("Sticky")),
    (STATUS_MODERATION, _("Moderation")),
    )


class MetaData(models.Model):
    """
    Abstract model that provides meta data for content.
    """
    title = models.CharField(_("Title"), max_length=256)
    slug = models.SlugField(_("URL"), max_length=256, blank=True, unique_for_date="publish_date")
    description = models.TextField(_("Description"), blank=True)
    status = models.IntegerField(_("Status"), choices=STATUS_CHOICES, default=STATUS_PUBLISHED)
    user = models.ForeignKey(User, blank=True, null=True, verbose_name=_("Author"), related_name="%(app_label)s_%(class)s_user")
    publish_date = models.DateTimeField(_("Published from"), default=datetime.now(), help_text=_("With published checked, won't be shown until this time"), blank=True)
    updated_date = models.DateTimeField(_("Updated date"), null=True, blank=True)
    login_required = models.BooleanField(verbose_name=_("Login required"), default=False, help_text=_("Enable this if users must login before access with this objects."))
    allow_comments = models.BooleanField(_("allow comments"), default=True)
    allow_pics = models.BooleanField(_("allow pics"), default=False)
    allow_docs = models.BooleanField(_("allow docs"), default=False)
    comments = models.IntegerField(blank=True, null=True)
    docs = models.IntegerField(blank=True, null=True)
    pics = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = _("MetaData")
        verbose_name_plural = _("MetaDatas")
        ordering = ("-publish_date",)
        abstract = True

    objects = Manager()
    search_fields = {"title": 5}
    slug_detail = 'metadata_detail'

    def delete(self, *args, **kwargs):
        self.status = STATUS_DELETE
        self.save()

    def save(self, *args, **kwargs):
        """
        Set default for ``description`` if none
        given.
        """
        if not self.description:
            try:
                self.description = strip_tags(self.description_from_content())
            except:
                self.description = ""
        self.updated_date = datetime.now()
        if not self.slug:
            if not self.id:
                super(MetaData, self).save(*args, **kwargs)
            self.slug = self.id
        super(MetaData, self).save(*args, **kwargs)

    def description_from_content(self):
        """
        Returns the first paragraph of the first content-like field.
        """
        description = ""
        # Use the first TextField if none found.
        if not description:
            for field in self._meta.fields:
                if isinstance(field, models.TextField) and field.name != "description":
                    description = getattr(self, field.name)
                    if description:
                        break
                        # Fall back to the title if description couldn't be determined.
        if not description:
            description = self.title
            # Strip everything after the first paragraph or sentence.
        for end in ("</p>", "<br />", "\n", ". "):
            if end in description:
                description = description.split(end)[0] + end
                break
        else:
            description = truncatewords_html(description, 256)
        return description

    @permalink
    def get_absolute_url(self):
        if self.slug:
            slug = self.slug
        else:
            slug = self.pk
        return (self.slug_detail, (), {
            'year': self.publish_date.year,
            'month': self.publish_date.strftime('%b').lower(),
            'day': self.publish_date.day,
            'slug': slug})

    def is_editable(self, request):
        """
        Restrict in-line editing to the objects's owner and superusers.
        """
        return request.user.is_superuser or request.user == self.user

    def admin_link(self):
        return "<a href='%s'>%s</a>" % (self.get_absolute_url(), _("View on site"))

    admin_link.allow_tags = True
    admin_link.short_description = ""

class MetaName(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=100)
    name_en = models.CharField(verbose_name=_("Name(English"), max_length=100, blank=True, null=True)
    enabled = models.BooleanField(verbose_name=_("Enabled in system"), default=True)
    description = models.TextField(verbose_name=_("Description"), blank=True, null=True)
    description_en = models.TextField(verbose_name=_("Description(English)"), blank=True, null=True)
    slug = models.CharField(verbose_name=_('URL-identifier'), max_length=100, blank=True, null=True)
    order_in_list = models.IntegerField(_('Order in list'), default=0)

    class Meta:
        ordering = ['name', ]
        abstract = True

    def __unicode__(self):
        return self.name

    @property
    def get_name(self):
        try:
            if get_language() == 'en':
                if self.name_en:
                    return self.name_en
            return self.name
        except :
            return self.name

    def get_description(self):
        try:
            if get_language() == 'en':
                if self.description_en:
                    return self.description_en
        except :
            pass
        return self.description

    def save(self, *args, **kwargs):
        if not self.slug:
            if not self.id:
                super(MetaName, self).save(*args, **kwargs)
            self.slug = self.id
        else:
            self.slug = str(self.slug).strip().replace(' ','-')
        super(MetaName, self).save(*args, **kwargs)


class Tree(MetaName):
    """
    Main nodes tree
    """
    parent = models.ForeignKey('self', verbose_name=_("Parent"), blank=True, null=True, related_name="children")
    ordering = models.IntegerField(_("Ordering"), default=0, help_text=_("Override alphabetical order in tree display"))
    rootnode = models.BooleanField(_('Root node'), default=False)
    login_required = models.BooleanField(verbose_name=_("Login required"), default=False, help_text=_("Enable this if users must login before access with this objects."))

    class Meta:
        ordering = ['ordering', ]
        verbose_name = _("Tree")
        verbose_name_plural = _("Trees")
        abstract = True

    def _recurse_for_parents(self, node):
        p_list = []
        if node.parent_id:
            p = node.parent
            p_list.append(p)
            if p != self:
                more = self._recurse_for_parents(p)
                p_list.extend(more)
        if node == self and p_list:
            p_list.reverse()
        return p_list

    def get_absolute_url(self):
        parents = self._recurse_for_parents(self)
        slug_list = [node.slug for node in parents]
        if slug_list:
            slug_list = "/".join(slug_list) + "/"
        else:
            slug_list = ""
        return reverse(self.slug_detail,
            kwargs={'parent_slugs': slug_list, 'slug': self.slug})

    def get_separator(self):
        return ' > '

    def _parents_repr(self):
        name_list = [node.title for node in self._recurse_for_parents(self)]
        return self.get_separator().join(name_list)

    _parents_repr.short_description = _("Tree parents")

    def get_url_name(self):
        # Get all the absolute URLs and names for use in the site navigation.
        name_list = []
        url_list = []
        for node in self._recurse_for_parents(self):
            name_list.append(node.title)
            url_list.append(node.get_absolute_url())
        name_list.append(self.title)
        url_list.append(self.get_absolute_url())
        return zip(name_list, url_list)

    def __unicode__(self):
        name_list = [node.title for node in self._recurse_for_parents(self)]
        name_list.append(self.title)
        return self.get_separator().join(name_list)

    def save(self, *args, **kwargs):
        if self.id:
            if self.parent and self.parent_id == self.id:
                raise ValidationError(_("You must not save a category in itself!"))
            for p in self._recurse_for_parents(self):
                if self.id == p.id:
                    raise ValidationError(_("You must not save a category in itself!"))
        super(Tree, self).save(*args, **kwargs)

    def _flatten(self, L):
        """
        Taken from a python newsgroup post
        """
        if type(L) != type([]):
            return [L]
        if not L:
            return L
        return self._flatten(L[0]) + self._flatten(L[1:])

    def _recurse_for_children(self, node, only_active=False):
        children = [node]
        for child in node.children.all():
            if child != self:
                if not only_active:
                    children_list = self._recurse_for_children(child, only_active=only_active)
                    children.append(children_list)
        return children

    def get_all_children(self, only_active=False, include_self=False):
        """
        Gets a list of all of the children categories.
        """
        children_list = self._recurse_for_children(self, only_active=only_active)
        if include_self:
            ix = 0
        else:
            ix = 1
        flat_list = self._flatten(children_list[ix:])
        return flat_list


class Tag(models.Model):
    """
    Model for Tags
    """
    name = models.CharField(_('Name'), max_length=40, unique=True, db_index=True)
    slug = models.SlugField(_("URL"), max_length=40, unique=True)
    follow = models.PositiveIntegerField(default=0, editable=False)


    class Meta:
        ordering = ('name',)
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Tag, self).save(*args, **kwargs)

    def lettercount(self):
        return Tag.objects.filter(name__startswith=self.name[0]).count()

    def __unicode__(self):
        return self.name

    def followers_count(self):
        ctype = ContentType.objects.get_for_model(self)
        return Follow.objects.filter(content_type=ctype,object_id=self.pk).count()

    def followers(self):
        ctype = ContentType.objects.get_for_model(self)
        users = Follow.objects.filter(content_type=ctype,object_id=self.pk).values_list('user',flat=True)
        return User.objects.filter(pk__in=users)

    @permalink
    def get_absolute_url(self):
        return "tag_detail", (), {'slug': self.slug}


class MetaLink(models.Model):
    # Generic Foreign Key Fields
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(_('object ID'), null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    primary = models.BooleanField(_('Is primary'), default=False)

    class Meta:
        abstract = True

    objects = MetaLinkManager()

    def get_content_object(self):
        """
        Wrapper around the GenericForeignKey due to compatibility reasons
        and due to ``list_display`` limitations.
        """
        return self.content_object

    def __unicode__(self):
        if len(self.description) > 50:
            return self.description[:50] + "..."
        return self.description[:50]

    def admin_link(self):
        return "<a href='%s'>%s</a>" % (self.get_absolute_url(), _("View on site"))

    admin_link.allow_tags = True
    admin_link.short_description = ""


DOC_FILE = 0
DOC_IMAGE = 1

DOC_TYPE = (
    (DOC_FILE, _("File")),
    (DOC_IMAGE, _("Image")),
    )


class MetaFile(models.Model):
    publish_date = models.DateTimeField(_("Published from"), default=datetime.now())
    user = models.ForeignKey(User, blank=True, null=True, verbose_name=_("Author"), related_name="%(class)s_user")
    description = models.CharField(verbose_name=_("Description"), max_length=256, blank=True)
    size = models.IntegerField(editable=False, null=True, blank=True)
    ordering = models.IntegerField(_("Ordering"), default=0, help_text=_("Override alphabetical order in list display"))
    locked = models.BooleanField(_('Is locked'), default=False)

    class Meta:
        abstract = True

class MetaIP(models.Model):
    ip = models.IPAddressField(verbose_name=_('IP'), null=True, blank=True)
    user_agent = models.CharField(verbose_name=_('User Agent'), null=True, blank=True, max_length=255)

    class Meta:
        abstract = True


class Doc(MetaLink, MetaFile):
    filetype = models.IntegerField(_("Doc type"), choices=DOC_TYPE, default=DOC_FILE)
    file = models.FileField(_("File"), upload_to="doc/%Y/%m/%d/", max_length=1024, blank=True)

    class Meta:
        ordering = ['ordering', ]
        verbose_name = _("Doc")
        verbose_name_plural = _("Docs")

    objects = MetaLinkManager()

    def save(self, *args, **kwargs):
        try:
            docs = Doc.objects.metalinks_for_object(self.content_object)
            if self.pk:
                docs = docs.exclude(pk=self.pk)
            if settings.DOC_MAX_PER_OBJECT > 1:
                if self.primary:
                    docs = docs.filter(primary=True)
                    docs.update(primary=False)
            else:
                docs.delete()
        except :
            pass
        fullpath = os.path.join(settings.MEDIA_ROOT, self.file.field.upload_to, self.file.path)
        self.size = os.path.getsize(fullpath)
        super(Doc, self).save(*args, **kwargs)

    @permalink
    def get_absolute_url(self):
        return os.path.join(settings.MEDIA_URL, self.file.url)

    def get_file_link(self):
        return os.path.join(settings.MEDIA_URL, self.file.url)

    def get_del_url(self):
        return reverse("doc_del", self.id)

    def get_edit_url(self):
        return reverse("doc_edit", self.id)


class Pic(MetaLink, MetaFile):
    pic = models.ImageField(verbose_name=_("Image"), max_length=1024, upload_to="pic/%Y/%m/%d/", blank=True)
    source = models.URLField(verbose_name=_("Source"), max_length=256, blank=True)

    objects = MetaLinkManager()

    class Meta:
        ordering = ['publish_date', ]
        verbose_name = _("Pic")
        verbose_name_plural = _("Pics")

    def __unicode__(self):
        return _(u'Pic for %(type)s: %(obj)s') % {'type': unicode(self.content_type), 'obj': unicode(self.content_object)}

    def get_file_link(self):
        return os.path.join(settings.MEDIA_URL, self.pic.url)

    def save(self, *args, **kwargs):
        pics = Pic.objects.metalinks_for_object(self.content_object)
        if self.pk:
            pics = pics.exclude(pk=self.pk)
        if settings.PIC_MAX_PER_OBJECT > 1:
            if self.primary:
                pics = pics.filter(primary=True)
                pics.update(primary=False)
        else:
            pics.delete()
        try:
            remove_thumbnails(self.pic.path)
        except:
            pass
        fullpath = get_path_from_url(self.pic.url)
        self.size = os.path.getsize(fullpath)
        super(Pic, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            remove_thumbnails(self.pic.path)
            remove_file(self.pic.path)
        except:
            pass
        super(Pic, self).delete(*args, **kwargs)

    def create_thumbnail(self, size, quality=None):
        try:
            orig = self.pic.storage.open(self.pic.name, 'rb').read()
            image = Image.open(StringIO(orig))
        except IOError:
            return  # What should we do here?  Render a "sorry, didn't work" img?
        quality = quality or settings.PIC_THUMB_QUALITY
        (w, h) = image.size
        if w != size or h != size:
            if w > h:
                diff = (w - h) / 2
                image = image.crop((diff, 0, w - diff, h))
            else:
                diff = (h - w) / 2
                image = image.crop((0, diff, w, h - diff))
            if image.mode != "RGB":
                image = image.convert("RGB")
            image = image.resize((size, size), settings.PIC_RESIZE_METHOD)
            thumb = StringIO()
            image.save(thumb, settings.PIC_THUMB_FORMAT, quality=quality)
            thumb_file = ContentFile(thumb.getvalue())
        else:
            thumb_file = ContentFile(orig)
        thumb = self.pic.storage.save(self.pic_name(size), thumb_file)

    def get_del_url(self):
        return "pic_del", (), {'object_id': self.pk}
        #return reverse("pic_del", self.id)

    def get_edit_url(self):
        return reverse("pic_edit", self.pk)

    def get_view_url(self):
        return reverse("pic_view", self.pk)

    def get_editor_url(self):
        return reverse("pic_editor", self.pk)


class JComment(MetaLink, MetaIP):
    """
    A threaded comment which must be associated with an instance of
    ``django.contrib.auth.models.User``.  It is given its hierarchy by
    a nullable relationship back on itself named ``parent``.
    It also includes two Managers: ``objects``, which is the same as the normal
    ``objects`` Manager with a few added utility functions (see above), and
    ``public``, which has those same utility functions but limits the QuerySet to
    only those values which are designated as public (``is_public=True``).
    """
    # Hierarchy Field
    parent = models.ForeignKey('self', null=True, blank=True, default=None, related_name='children')
    # User Field
    user = models.ForeignKey(User)
    # Date Fields
    publish_date = models.DateTimeField(_('date/time published'), default=datetime.now)
    updated_date = models.DateTimeField(_('date/time updated'), null=True, blank=True)
    # Meat n' Potatoes
    comment = models.TextField(_('comment'))
    # Status Fields
    status = models.IntegerField(_("Status"), choices=STATUS_CHOICES, default=STATUS_PUBLISHED)
    # Extra Field
#    ip_address = models.IPAddressField(_('IP address'), null=True, blank=True)

    objects = JCommentManager()
    public = PublicJCommentManager()

    def __unicode__(self):
        if len(self.comment) > 50:
            return self.comment[:50] + "..."
        return self.comment[:50]

    def save(self, **kwargs):
        self.updated_date = datetime.now()
        super(JComment, self).save(**kwargs)

    def get_base_data(self, show_dates=True):
        """
        Outputs a Python dictionary representing the most useful bits of
        information about this particular object instance.
        This is mostly useful for testing purposes, as the output from the
        serializer changes from run to run.  However, this may end up being
        useful for JSON and/or XML data exchange going forward and as the
        serializer system is changed.
        """
        to_return = {
            'content_object': self.content_object,
            'parent': self.parent,
            'user': self.user,
            'comment': self.comment,
            'status': self.status,
            'ip_address': self.ip_address,
            }
        if show_dates:
            to_return['publish_date'] = self.publish_date
            to_return['updated_date'] = self.updated_date
        return to_return

    class Meta:
        ordering = ('-publish_date',)
        verbose_name = _("Threaded Comment")
        verbose_name_plural = _("Threaded Comments")
        get_latest_by = "publish_date"


class Follow(models.Model):
    """
    Lets a user follow the activities of any specific actor
    """
    user = models.ForeignKey(User)

    content_type = models.ForeignKey(ContentType)
    object_id = models.CharField(max_length=255)
    actor = GenericForeignKey()

    objects = FollowManager()

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')
        verbose_name = _("Follow")
        verbose_name_plural = _("Follows")

    def __unicode__(self):
        return u'%s -> %s' % (self.user, self.actor)

NOTICE_UNKNOWN = 0
NOTICE_SYSTEM = 1
NOTICE_VIDEO = 2
NOTICE_TAG = 3
NOTICE_ACCOUNT = 4
NOTICE_PROFILE = 5

NOTICE_CHOICES = (
    (NOTICE_UNKNOWN, _("Unknown")),
    (NOTICE_SYSTEM, _("System")),
    (NOTICE_VIDEO, _("Video")),
    (NOTICE_TAG, _("Tag")),
    (NOTICE_ACCOUNT, _("Account")),
    (NOTICE_PROFILE, _("Profile")),
    )


class Notice(MetaLink, MetaIP):
    """
    User notification model
    """
    user = models.ForeignKey(User)
    notice_type = models.IntegerField(_("Notice Type"), choices=NOTICE_CHOICES, default=NOTICE_UNKNOWN)
    sender = models.ForeignKey(User, related_name='notice_sender')
    verb = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(default=datetime.now)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _("Notice")
        verbose_name_plural = _("Notices")

class Message(MetaIP):
    """
    A private message from user to user
    """
    subject = models.CharField(_("Subject"), max_length=120, blank=True, null=True)
    body = models.TextField(_("Body"))
    sender = models.ForeignKey(User, related_name='sent_messages', verbose_name=_("Sender"))
    recipient = models.ForeignKey(User, related_name='received_messages', null=True, blank=True, verbose_name=_("Recipient"))
    parent_msg = models.ForeignKey('self', related_name='next_messages', null=True, blank=True, verbose_name=_("Parent message"))
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

    def __unicode__(self):
        if self.subject is not None:
            return self.subject
        if self.body is not None:
            return self.body[:40]
        return None

    def get_absolute_url(self):
        return 'messages_detail', [self.id]
    get_absolute_url = models.permalink(get_absolute_url)

    def save(self, **kwargs):
        if not self.id:
            self.sent_at = datetime.now()
        super(Message, self).save(**kwargs)

    class Meta:
        ordering = ['-sent_at']
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")


ACTION_UNKNOWN = 0
ACTION_SYSTEM = 1
ACTION_ADDED = 2
ACTION_COMMENTED = 3
ACTION_FOLLOWED = 4
ACTION_LIKED = 5

ACTION_CHOICES = (
    (ACTION_UNKNOWN, _("Unknown")),
    (ACTION_SYSTEM, _("System")),
    (ACTION_ADDED, _("Added")),
    (ACTION_COMMENTED, _("Commented")),
    (ACTION_FOLLOWED, _("Followed")),
    (ACTION_LIKED, _("Liked")),
    )

class Action(MetaLink,MetaIP):
    """
    Model Activity of User
    """
    user = models.ForeignKey(User, related_name='actions')
    action_type = models.IntegerField(_("Action Type"), choices=ACTION_CHOICES, default=ACTION_UNKNOWN)
    verb = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(default=datetime.now)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _("Action")
        verbose_name_plural = _("Actions")

    @property
    def target_type(self):
        return ContentType.objects.get_for_model(self.content_object).model

    def __unicode__(self):
        return u'%s %s %s ago' % (self.user, self.verb, self.timesince())


    def timesince(self, now=None):
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the
        current timestamp.
        """
        from django.utils.timesince import timesince as timesince_
        return timesince_(self.timestamp, now)

    @models.permalink
    def get_absolute_url(self):
        return 'nnmware.core.views.detail', [self.pk]

def update_comment_count(sender, instance, **kwargs):
    what = instance.get_content_object()
    what.comments = JComment.public.all_for_object(what).count()
    what.updated_date = datetime.now()
    what.save()


def update_pic_count(sender, instance, **kwargs):
    what = instance.get_content_object()
    what.pics = Pic.objects.metalinks_for_object(what).count()
    what.save()


def update_doc_count(sender, instance, **kwargs):
    what = instance.get_content_object()
    what.docs = Doc.objects.metalinks_for_object(what).count()
    what.save()

signals.post_save.connect(update_comment_count, sender=JComment, dispatch_uid="nnmware_id")
signals.post_delete.connect(update_comment_count, sender=JComment, dispatch_uid="nnmware_id")
signals.post_save.connect(update_pic_count, sender=Pic, dispatch_uid="nnmware_id")
signals.post_delete.connect(update_pic_count, sender=Pic, dispatch_uid="nnmware_id")
signals.post_save.connect(update_doc_count, sender=Doc, dispatch_uid="nnmware_id")
signals.post_delete.connect(update_doc_count, sender=Doc, dispatch_uid="nnmware_id")

class VisitorHit(models.Model):
    user = models.ForeignKey(User, verbose_name=_('User'), blank=True, null=True)
    date = models.DateTimeField(verbose_name=_("Creation date"), default=datetime.now())
    session_key = models.CharField(max_length=40, verbose_name=_('Session key'))
    ip_address = models.CharField(max_length=20, verbose_name=_('IP'))
    hostname = models.CharField(max_length=100, verbose_name=_('Hostname'))
    user_agent = models.CharField(max_length=255, verbose_name=_('User-agent'))
    referrer = models.CharField(max_length=255, verbose_name=_('Referrer'))
    url = models.CharField(max_length=255, verbose_name=_('URL'))
    secure = models.BooleanField(_('Is secure'), default=False)

    class Meta:
        ordering = ['-date']
        verbose_name = _("Visitor hit")
        verbose_name_plural = _("Visitors hits")
