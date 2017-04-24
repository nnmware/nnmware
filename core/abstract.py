# nnmware(c)2012-2017

from __future__ import unicode_literals
from io import StringIO
import os
from PIL import Image
from uuid import uuid4

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.urls import reverse
from django.utils.timezone import now
from django.db import models
from django.db.models.manager import Manager
from django.utils.translation import ugettext_lazy as _
from django.utils.translation.trans_real import get_language

from nnmware.core.file import get_path_from_url
from nnmware.core.constants import GENDER_CHOICES, STATUS_CHOICES, STATUS_PUBLISHED, SKILL_UNKNOWN, SKILL_CHOICES, \
    EDU_UNKNOWN, EDU_CHOICES
from nnmware.core.imgutil import remove_thumbnails, remove_file, make_thumbnail
from nnmware.core.managers import AbstractContentManager, PublicNnmcommentManager, AbstractActiveManager
from nnmware.core.fields import std_text_field, std_url_field
from nnmware.core.utils import setting, current_year, tuplify

DEFAULT_IMG = os.path.join(settings.MEDIA_URL, setting('DEFAULT_IMG', 'generic.png'))
DOC_MAX_PER_OBJECT = setting('DOC_MAX_PER_OBJECT', 42)
IMG_MAX_PER_OBJECT = setting('IMG_MAX_PER_OBJECT', 42)
IMG_THUMB_QUALITY = setting('IMG_THUMB_QUALITY', 85)
IMG_THUMB_FORMAT = setting('IMG_THUMB_FORMAT', 'JPEG')
IMG_RESIZE_METHOD = setting('IMG_RESIZE_METHOD', Image.ANTIALIAS)
EDUCATION_END = map(tuplify, range(current_year - 55, current_year + 1)[::-1])


class AbstractDate(models.Model):
    created_date = models.DateTimeField(_("Created date"), default=now)
    updated_date = models.DateTimeField(_("Updated date"), null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, **kwargs):
        self.updated_date = now()
        super(AbstractDate, self).save(**kwargs)


class AbstractContent(models.Model):
    # Generic Foreign Key Fields
    content_type = models.ForeignKey(ContentType, null=True, blank=True,
                                     related_name="%(app_label)s_%(class)s_cntype", on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(_('object ID'), null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    primary = models.BooleanField(_('Is primary'), default=False)

    class Meta:
        abstract = True

    objects = AbstractContentManager()

    def __str__(self):
        # noinspection PyBroadException
        try:
            return "%s - %s " % (self.content_object.get_name, self.pk)
        except:
            return None

    def get_content_object(self):
        return self.content_object


DOC_FILE = 0
DOC_IMAGE = 1

DOC_TYPE = (
    (DOC_FILE, _("File")),
    (DOC_IMAGE, _("Image")),
)


class AbstractFile(AbstractDate):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, verbose_name=_("Author"),
                             related_name="%(class)s_f_user", on_delete=models.CASCADE)
    description = std_text_field(_("Description"))
    size = models.IntegerField(editable=False, null=True, blank=True)
    position = models.PositiveSmallIntegerField(verbose_name=_('Priority'), db_index=True, default=0, blank=True)
    locked = models.BooleanField(_('Is locked'), default=False)

    class Meta:
        abstract = True


class Pic(AbstractContent, AbstractFile):
    pic = models.ImageField(verbose_name=_("Image"), max_length=1024, upload_to="pic/%Y/%m/%d/", blank=True)
    source = models.URLField(verbose_name=_("Source"), max_length=256, blank=True)

    objects = AbstractContentManager()

    class Meta:
        ordering = ['created_date', ]
        verbose_name = _("Pic")
        verbose_name_plural = _("Pics")

    def __str__(self):
        return _('Pic for %(type)s: %(obj)s') % {'type': self.content_type, 'obj': self.content_object}

    def get_file_link(self):
        return os.path.join(settings.MEDIA_URL, self.pic.url)

    def save(self, *args, **kwargs):
        pics = Pic.objects.for_object(self.content_object)
        if self.pk:
            pics = pics.exclude(pk=self.pk)
        if IMG_MAX_PER_OBJECT > 1:
            if self.primary:
                pics = pics.filter(primary=True)
                pics.update(primary=False)
        else:
            pics.delete()
        # noinspection PyBroadException
        try:
            remove_thumbnails(self.pic.path)
        except:
            pass
        fullpath = get_path_from_url(self.pic.url)
        self.size = os.path.getsize(fullpath)
        super(Pic, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # noinspection PyBroadException
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
        except IOError as ioerr:
            return  # What should we do here?  Render a "sorry, didn't work" img?
        quality = quality or IMG_THUMB_QUALITY
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
            image = image.resize((size, size), IMG_RESIZE_METHOD)
            thumb = StringIO()
            image.save(thumb, IMG_THUMB_FORMAT, quality=quality)
            thumb_file = ContentFile(thumb.getvalue())
        else:
            thumb_file = ContentFile(orig)
        thumb = self.pic.storage.save(self.pic_name(size), thumb_file)

    def get_del_url(self):
        return "pic_del", (), {'object_id': self.pk}

    def get_edit_url(self):
        return reverse("pic_edit", args=[self.pk])

    def get_view_url(self):
        return reverse("pic_view", args=[self.pk])

    def get_editor_url(self):
        return reverse("pic_editor", args=[self.pk])

    def slide_thumbnail(self):
        if self.pic:
            path = self.pic.url
            tmb = make_thumbnail(path, width=60, height=60, aspect=1)
        else:
            tmb = '/static/img/icon-no.gif"'
            path = '/static/img/icon-no.gif"'
        return '<a target="_blank" href="%s"><img src="%s" /></a>' % (path, tmb)

    slide_thumbnail.allow_tags = True


class PicsMixin(object):

    @property
    def main_image(self):
        # noinspection PyBroadException
        try:
            return self.allpics[0].pic.url
        except:
            return DEFAULT_IMG

    @property
    def allpics(self):
        return Pic.objects.for_object(self).order_by('-primary')

    @property
    def images(self):
        return Pic.objects.for_object(self).order_by('position')

    @property
    def obj_pic(self):
        # noinspection PyBroadException
        try:
            return self.allpics[0]
        except:
            return None

    @property
    def pics_count(self):
        return self.allpics.count()


class AbstractTeaser(models.Model):
    teaser = models.CharField(verbose_name=_('Teaser'), max_length=255, db_index=True, blank=True)
    teaser_en = models.CharField(verbose_name=_('Teaser(English)'), max_length=255, blank=True,
                                 db_index=True)

    class Meta:
        abstract = True

    @property
    def get_teaser(self):
        if get_language() == 'en':
            if self.teaser_en:
                return self.teaser_en
        return self.teaser


class Unit(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name of unit'))

    class Meta:
        verbose_name = _("Unit")
        verbose_name_plural = _("Units")
        abstract = True

    def __str__(self):
        return "%s" % self.name


class Parameter(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name of parameter'))

    class Meta:
        verbose_name = _("Parameter")
        verbose_name_plural = _("Parameters")
        abstract = True

    def __str__(self):
        # noinspection PyBroadException
        try:
            return "%s (%s)" % (self.name, self.unit.name)
        except:
            return "%s" % self.name


class AbstractImg(models.Model):
    img = models.ImageField(verbose_name=_("Image"), max_length=1024, upload_to="img/%Y/%m/%d/", blank=True,
                            height_field='img_height', width_field='img_width')
    img_height = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Image height'))
    img_width = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Image height'))

    class Meta:
        abstract = True

    @property
    def avatar(self):
        if self.img:
            return self.img
        return None

    @property
    def get_avatar(self):
        if self.img:
            return self.avatar.url
        return setting('DEFAULT_AVATAR', 'noavatar.png')

    def delete(self, *args, **kwargs):
        # noinspection PyBroadException
        try:
            remove_thumbnails(self.img.path)
            remove_file(self.img.path)
        except:
            pass
        super(AbstractImg, self).delete(*args, **kwargs)

    def thumbnail(self):
        if self.img:
            path = self.img.url
            tmb = make_thumbnail(path, height=60, width=60)
            return '<a style="display:block;text-align:center;" target="_blank" href="%s"><img src="%s" /></a>' \
                   '<p style="text-align:center;margin-top:5px;">%sx%s px</p>' % (path, tmb, self.img_width,
                                                                                  self.img_height)
        return "No image"
    thumbnail.allow_tags = True
    thumbnail.short_description = 'Thumbnail'


class AbstractName(AbstractImg, PicsMixin):
    name = models.CharField(verbose_name=_("Name"), max_length=255, blank=True, db_index=True, default='')
    name_en = models.CharField(verbose_name=_("Name(English"), max_length=255, blank=True, db_index=True, default='')
    enabled = models.BooleanField(verbose_name=_("Enabled in system"), default=True, db_index=True)
    description = models.TextField(verbose_name=_("Description"), blank=True, default='')
    description_en = models.TextField(verbose_name=_("Description(English)"), blank=True, default='')
    slug = models.CharField(verbose_name=_('URL-identifier'), max_length=100, blank=True, db_index=True, default='')
    position = models.PositiveSmallIntegerField(verbose_name=_('Priority'), db_index=True, default=0, blank=True)
    docs = models.IntegerField(blank=True, null=True)
    pics = models.IntegerField(blank=True, null=True)
    views = models.IntegerField(blank=True, null=True)
    comments = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['position', 'name']
        abstract = True

    objects = AbstractActiveManager()

    def __str__(self):
        return self.name

    @property
    def get_name(self):
        # noinspection PyBroadException
        try:
            if get_language() == 'en':
                if self.name_en:
                    return self.name_en
            return self.name
        except:
            return self.name

    def get_description(self):
        # noinspection PyBroadException
        try:
            if get_language() == 'en':
                if self.description_en:
                    return self.description_en
        except:
            pass
        return self.description

    def save(self, *args, **kwargs):
        if not self.slug:
            if not self.id:
                super(AbstractName, self).save(*args, **kwargs)
            self.slug = self.id
        else:
            self.slug = str(self.slug).strip().replace(' ', '-')
        super(AbstractName, self).save(*args, **kwargs)


class Material(AbstractName):
    pass

    class Meta:
        verbose_name = _("Material")
        verbose_name_plural = _("Materials")
        abstract = True

    def __str__(self):
        return self.name


class AbstractColor(AbstractName):
    pass

    class Meta:
        verbose_name = _("Color")
        verbose_name_plural = _("Colors")
        abstract = True

    def __str__(self):
        return self.name


class Tree(AbstractName):
    """
    Main nodes tree
    """
    parent = models.ForeignKey('self', verbose_name=_("Parent"), blank=True, null=True, related_name="children",
                               on_delete=models.CASCADE)
    rootnode = models.BooleanField(_('Root node'), default=False)
    login_required = models.BooleanField(verbose_name=_("Login required"), default=False,
                                         help_text=_("Enable this if users must login before access with this objects."))
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_('Category Admins'),
                                    related_name='%(app_label)s_%(class)s_adm', blank=True)

    class Meta:
        ordering = ['position', ]
        verbose_name = _("Tree")
        verbose_name_plural = _("Trees")
        abstract = True

    def item(self):
        if self.rootnode:
            return False
        return True

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

    def get_root_category(self, node):
        if node.parent:
            p = node.parent
            if p != self:
                return self.get_root_category(p)
        return node

    def root_category(self):
        return self.get_root_category(self)

    def get_absolute_url(self):
        parents = self._recurse_for_parents(self)
        slug_list = [node.slug for node in parents]
        if slug_list:
            slug_list = "/".join(slug_list) + "/"
        else:
            slug_list = ""
        return reverse(self.slug_detail, kwargs={'parent_slugs': slug_list, 'slug': self.slug})

    @property
    def get_separator(self):
        return ' > '

    def _parents_repr(self):
        name_list = [node.name for node in self._recurse_for_parents(self)]
        return self.get_separator.join(name_list)

    _parents_repr.short_description = _("Tree parents")

    def get_url_name(self):
        # Get all the absolute URLs and names for use in the site navigation.
        name_list = []
        url_list = []
        for node in self._recurse_for_parents(self):
            name_list.append(node.name)
            url_list.append(node.get_absolute_url())
        name_list.append(self.name)
        url_list.append(self.get_absolute_url())
        return zip(name_list, url_list)

    def get_root_catid(self):
        if self.parent_id:
            catidlist = self._recurse_for_parents(self)
            return [catidlist[0].name, catidlist[0].position]
        return [self.name, self.position]

    @property
    def get_all_ids(self):
        id_list = []
        for node in self._recurse_for_parents(self):
            id_list.append(node.pk)
        id_list.append(self.pk)
        return id_list

    def __str__(self):
        name_list = [node.name for node in self._recurse_for_parents(self)]
        name_list.append(self.name)
        return self.get_separator.join(name_list)

    def save(self, *args, **kwargs):
        if self.id:
            if self.parent and self.parent_id == self.id:
                raise ValidationError(_("You must not save a category in itself!"))
            for p in self._recurse_for_parents(self):
                if self.id == p.id:
                    raise ValidationError(_("You must not save a category in itself!"))
        super(Tree, self).save(*args, **kwargs)

    def _flatten(self, ll):
        """
        Taken from a python newsgroup post
        """
        if not isinstance(ll, list):
            return [ll]
        if not ll:
            return ll
        return self._flatten(ll[0]) + self._flatten(ll[1:])

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


class Doc(AbstractContent, AbstractFile):
    filetype = models.IntegerField(_("Doc type"), choices=DOC_TYPE, default=DOC_FILE)
    doc = models.FileField(_("File"), upload_to="doc/%Y/%m/%d/", max_length=1024, blank=True)

    class Meta:
        ordering = ['position', ]
        verbose_name = _("Doc")
        verbose_name_plural = _("Docs")

    objects = AbstractContentManager()

    def save(self, *args, **kwargs):
        # noinspection PyBroadException
        try:
            docs = Doc.objects.for_object(self.content_object)
            if self.pk:
                docs = docs.exclude(pk=self.pk)
            if DOC_MAX_PER_OBJECT > 1:
                if self.primary:
                    docs = docs.filter(primary=True)
                    docs.update(primary=False)
            else:
                docs.delete()
        except:
            pass
        fullpath = os.path.join(settings.MEDIA_ROOT, self.doc.field.upload_to, self.doc.path)
        self.size = os.path.getsize(fullpath)
        super(Doc, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # noinspection PyBroadException
        try:
            remove_file(self.doc.path)
        except:
            pass
        super(Doc, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(os.path.join(settings.MEDIA_URL, self.doc.url))

    def get_file_link(self):
        return os.path.join(settings.MEDIA_URL, self.doc.url)

    def get_del_url(self):
        return reverse("doc_del", args=[self.id])

    def get_edit_url(self):
        return reverse("doc_edit", args=[self.id])


class AbstractIP(models.Model):
    ip = models.GenericIPAddressField(verbose_name=_('IP'), null=True, blank=True)
    user_agent = models.CharField(verbose_name=_('User Agent'), blank=True, max_length=255, default='')

    class Meta:
        abstract = True


class AbstractOrder(AbstractImg):
    position = models.PositiveSmallIntegerField(verbose_name=_('Priority'), db_index=True, default=0, blank=True)
    name_en = std_text_field(_('English name'))

    class Meta:
        ordering = ['position', ]
        abstract = True

    def __str__(self):
        return "%s" % self.name


class AbstractSkill(AbstractOrder):
    level = models.IntegerField(_('Level'), choices=SKILL_CHOICES, blank=True, null=True, default=SKILL_UNKNOWN)

    class Meta:
        abstract = True

    def __str__(self):
        return "%s :: %s " % (self.skill.name, self.get_level_display())


class AbstractNnmwareProfile(AbstractDate, AbstractImg, PicsMixin):
    uid = models.UUIDField(default=uuid4, editable=False, db_index=True)
    main = models.BooleanField(_('Main profile'), default=False)
    first_name = std_text_field(_('First Name'), max_length=50)
    middle_name = std_text_field(_('Middle Name'), max_length=50)
    last_name = std_text_field(_('Last Name'), max_length=50)
    viewcount = models.PositiveIntegerField(default=0, editable=False)
    enabled = models.BooleanField(verbose_name=_("Enabled in system"), default=False)
    birthdate = models.DateField(verbose_name=_('Date birth'), blank=True, null=True)
    gender = models.CharField(verbose_name=_("Gender"), max_length=1, choices=GENDER_CHOICES, blank=True)
    is_employer = models.BooleanField(verbose_name=_("Account is employer"), default=False)
    is_public = models.BooleanField(verbose_name=_("Account is public"), default=False)
    agent_img = models.ImageField(verbose_name=_("Agent avatar"), max_length=1024, upload_to="img/%Y/%m/%d/",
                                  blank=True, height_field='agent_img_height', width_field='agent_img_width')
    agent_img_height = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Agent avatar height'))
    agent_img_width = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Agent avatar height'))

    @property
    def events_count(self):
        return self.events.count()

    @property
    def get_name(self):
        if self.first_name and self.last_name:
            return self.first_name + ' ' + self.last_name
        else:
            return self.user.username

    def __str__(self):
        return self.get_name

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        abstract = True

    def get_absolute_url(self):
        return reverse('employer_view', args=[self.pk])

    @property
    def get_agent_avatar(self):
        if self.agent_img:
            return self.agent_img.url
        return setting('DEFAULT_AVATAR', 'noavatar.png')


class AbstractOffer(AbstractImg):
    created_date = models.DateTimeField(_("Created date"), default=now)
    start_date = models.DateTimeField(_("Start date"), default=now)
    end_date = models.DateTimeField(_("End date"), default=now)
    title = std_text_field(_('Title'))
    text = models.TextField(verbose_name=_("Offer text"), blank=True)
    enabled = models.BooleanField(verbose_name=_("Enabled"), default=False)
    slug = models.CharField(verbose_name=_('URL-identifier'), max_length=100, blank=True)
    position = models.PositiveSmallIntegerField(verbose_name=_('Priority'), db_index=True, default=0, blank=True)

    objects = Manager()

    class Meta:
        verbose_name = _('Special Offer')
        verbose_name_plural = _('Special Offers')
        abstract = True


class AbstractWorkTime(models.Model):
    mon_on = models.TimeField(verbose_name=_('Monday time from'), blank=True, null=True)
    mon_off = models.TimeField(verbose_name=_('Monday time to'), blank=True, null=True)
    mon_break_on = models.TimeField(verbose_name=_('Monday break from'), blank=True, null=True)
    mon_break_off = models.TimeField(verbose_name=_('Monday break to'), blank=True, null=True)
    mon_any = models.BooleanField(verbose_name=_('Monday any time'), default=False)
    tue_on = models.TimeField(verbose_name=_('Tuesday time from'), blank=True, null=True)
    tue_off = models.TimeField(verbose_name=_('Tuesday time to'), blank=True, null=True)
    tue_break_on = models.TimeField(verbose_name=_('Tuesday break from'), blank=True, null=True)
    tue_break_off = models.TimeField(verbose_name=_('Tuesday break to'), blank=True, null=True)
    tue_any = models.BooleanField(verbose_name=_('Tuesday any time'), default=False)
    wed_on = models.TimeField(verbose_name=_('Wednesday time from'), blank=True, null=True)
    wed_off = models.TimeField(verbose_name=_('Wednesday time to'), blank=True, null=True)
    wed_break_on = models.TimeField(verbose_name=_('Wednesday break from'), blank=True, null=True)
    wed_break_off = models.TimeField(verbose_name=_('Wednesday break to'), blank=True, null=True)
    wed_any = models.BooleanField(verbose_name=_('Wednesday any time'), default=False)
    thu_on = models.TimeField(verbose_name=_('Thursday time from'), blank=True, null=True)
    thu_off = models.TimeField(verbose_name=_('Thursday time to'), blank=True, null=True)
    thu_break_on = models.TimeField(verbose_name=_('Thursday break from'), blank=True, null=True)
    thu_break_off = models.TimeField(verbose_name=_('Thursday break to'), blank=True, null=True)
    thu_any = models.BooleanField(verbose_name=_('Thursday any time'), default=False)
    fri_on = models.TimeField(verbose_name=_('Friday time from'), blank=True, null=True)
    fri_off = models.TimeField(verbose_name=_('Friday time to'), blank=True, null=True)
    fri_break_on = models.TimeField(verbose_name=_('Friday break from'), blank=True, null=True)
    fri_break_off = models.TimeField(verbose_name=_('Friday break to'), blank=True, null=True)
    fri_any = models.BooleanField(verbose_name=_('Friday any time'), default=False)
    sat_on = models.TimeField(verbose_name=_('Saturday time from'), blank=True, null=True)
    sat_off = models.TimeField(verbose_name=_('Saturday time to'), blank=True, null=True)
    sat_break_on = models.TimeField(verbose_name=_('Saturday break from'), blank=True, null=True)
    sat_break_off = models.TimeField(verbose_name=_('Saturday break to'), blank=True, null=True)
    sat_any = models.BooleanField(verbose_name=_('Saturday any time'), default=False)
    sun_on = models.TimeField(verbose_name=_('Sunday time from'), blank=True, null=True)
    sun_off = models.TimeField(verbose_name=_('Sunday time to'), blank=True, null=True)
    sun_break_on = models.TimeField(verbose_name=_('Sunday break from'), blank=True, null=True)
    sun_break_off = models.TimeField(verbose_name=_('Sunday break to'), blank=True, null=True)
    sun_any = models.BooleanField(verbose_name=_('Sunday any time'), default=False)

    class Meta:
        verbose_name = _('Time of work')
        verbose_name_plural = _('Times of works')
        abstract = True


class UserMixin(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), on_delete=models.CASCADE)

    class Meta:
        abstract = True

    @property
    def get_user_name(self):
        # noinspection PyBroadException
        try:
            return self.user.get_name
        except:
            return self.user.username


class AbstractVendor(models.Model):
    name = models.CharField(_("Name of vendor"), max_length=200)
    name_en = models.CharField(_("Name of vendor(english)"), max_length=200, blank=True)
    website = std_url_field(_("URL"))
    description = models.TextField(_("Description of Vendor"), help_text=_("Description of Vendor"), default='',
                                   blank=True)

    class Meta:
        ordering = ['name', 'website']
        verbose_name = _("Vendor")
        verbose_name_plural = _("Vendors")
        abstract = True

    def __str__(self):
        return self.name


class AbstractNnmcomment(AbstractContent, AbstractIP, AbstractDate):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), null=True, blank=True,
                             related_name="%(app_label)s_%(class)s_user", on_delete=models.CASCADE)
    viewed = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_('Viewed'), blank=True,
                                    related_name="%(app_label)s_%(class)s_view_comments")
    comment = models.TextField(verbose_name=_('comment'), blank=True)
    parsed_comment = models.TextField(verbose_name=_('parsed content of comment'), blank=True)
    status = models.IntegerField(_("Status"), choices=STATUS_CHOICES, default=STATUS_PUBLISHED)

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
        ordering = ("-created_date",)
        get_latest_by = "created_date"
        abstract = True

    def __str__(self):
        if len(self.comment) > 50:
            return self.comment[:50] + "..."
        return self.comment[:50]

    public = PublicNnmcommentManager()


class AbstractLike(AbstractContent):
    """
    like = True
    dislike = False
    """
    like_dislike = models.NullBooleanField(verbose_name="Like-Dislike", default=None, db_index=True)

    class Meta:
        ordering = ('-pk',)
        verbose_name = "Like"
        verbose_name_plural = "Likes"
        abstract = True

    def __str__(self):
        return 'Likes for %s' % self.content_object


class AbstractEducation(models.Model):
    institution = std_text_field(_('Institution'))
    education_end = models.IntegerField(verbose_name=_('End of education'), choices=EDUCATION_END, default=current_year)
    education_type = models.IntegerField(verbose_name=_('Type of education'), choices=EDU_CHOICES, default=EDU_UNKNOWN)
    instructor = std_text_field(_('Instructor'))
    diploma = std_text_field(_('Diploma'))
    specialty = std_text_field(_('Specialty'))
    prof_edu = models.BooleanField(_('Profile education'), default=False)
    addon = std_text_field(_('Additional info'))
    position = models.PositiveSmallIntegerField(verbose_name=_('Priority'), db_index=True, default=0, blank=True)

    class Meta:
        verbose_name = _("Education")
        verbose_name_plural = _("Educations")
        abstract = True
