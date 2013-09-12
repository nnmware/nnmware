# -*- coding: utf-8 -*-
# Base abstract classed nnmware(c)2013

from django.conf import settings
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.timezone import now
from django.db import models
from django.db.models import permalink
from django.db.models.manager import Manager
from django.template.defaultfilters import truncatewords_html
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _
from django.utils.translation.trans_real import get_language
from nnmware.core.imgutil import remove_thumbnails, remove_file, make_thumbnail
from nnmware.core.managers import AbstractContentManager
from nnmware.core.fields import std_text_field, std_url_field, std_email_field
from django.utils.encoding import python_2_unicode_compatible

GENDER_CHOICES = (('F', _('Female')), ('M', _('Male')), ('N', _('None')))


class AbstractDate(models.Model):
    created_date = models.DateTimeField(_("Created date"), default=now)
    updated_date = models.DateTimeField(_("Updated date"), null=True, blank=True)

    class Meta:
        abstract = True


class AbstractTeaser(models.Model):
    teaser = models.CharField(verbose_name=_('Teaser'), max_length=255, db_index=True, blank=True, null=True)
    teaser_en = models.CharField(verbose_name=_('Teaser(English)'), max_length=255, blank=True, null=True,
                                 db_index=True)

    class Meta:
        abstract = True

    @property
    def get_teaser(self):
        if get_language() == 'en':
            if self.teaser_en:
                return self.teaser_en
        return self.teaser


@python_2_unicode_compatible
class Unit(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name of unit'))

    class Meta:
        verbose_name = _("Unit")
        verbose_name_plural = _("Units")
        abstract = True

    def __str__(self):
        return "%s" % self.name


@python_2_unicode_compatible
class Parameter(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name of parameter'))

    class Meta:
        verbose_name = _("Parameter")
        verbose_name_plural = _("Parameters")
        abstract = True

    def __str__(self):
        try:
            return "%s (%s)" % (self.name, self.unit.name)
        except:
            return "%s" % self.name


STATUS_DELETE = 0
STATUS_LOCKED = 1
STATUS_PUBLISHED = 2
STATUS_STICKY = 3
STATUS_MODERATION = 4
STATUS_DRAFT = 5

STATUS_CHOICES = (
    (STATUS_DELETE, _("Deleted")),
    (STATUS_LOCKED, _("Locked")),
    (STATUS_PUBLISHED, _("Published")),
    (STATUS_STICKY, _("Sticky")),
    (STATUS_MODERATION, _("Moderation")),
    (STATUS_DRAFT, _("Draft")),
)


class AbstractData(AbstractDate):
    """
    Abstract model that provides meta data for content.
    """
    title = models.CharField(_("Title"), max_length=256)
    slug = models.SlugField(_("URL"), max_length=256, blank=True, unique_for_date="created_date")
    description = models.TextField(_("Description"), blank=True)
    status = models.IntegerField(_("Status"), choices=STATUS_CHOICES, default=STATUS_PUBLISHED)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, verbose_name=_("Author"),
                             related_name="%(app_label)s_%(class)s_user")
    login_required = models.BooleanField(verbose_name=_("Login required"), default=False, help_text=_(
        "Enable this if users must login before access with this objects."))
    allow_comments = models.BooleanField(_("allow comments"), default=True)
    allow_pics = models.BooleanField(_("allow pics"), default=False)
    allow_docs = models.BooleanField(_("allow docs"), default=False)
    comments = models.IntegerField(blank=True, null=True)
    docs = models.IntegerField(blank=True, null=True)
    pics = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = _("AbstractData")
        verbose_name_plural = _("AbstractDatas")
        ordering = ("-created_date",)
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
        self.updated_date = now()
        if not self.slug:
            if not self.pk:
                super(AbstractData, self).save(*args, **kwargs)
            self.slug = self.pk
        super(AbstractData, self).save(*args, **kwargs)

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
            'year': self.created_date.year,
            'month': self.created_date.strftime('%b').lower(),
            'day': self.created_date.day,
            'slug': slug})

    def is_editable(self, request):
        """
        Restrict in-line editing to the object's owner and superusers.
        """
        return request.user.is_superuser or request.user == self.user

    def admin_link(self):
        return "<a href='%s'>%s</a>" % (self.get_absolute_url(), _("View on site"))

    admin_link.allow_tags = True
    admin_link.short_description = ""


class AbstractImg(models.Model):
    img = models.ImageField(verbose_name=_("Image"), max_length=1024, upload_to="pic/%Y/%m/%d/", blank=True)

    class Meta:
        abstract = True

    @property
    def ava(self):
        try:
            return self.img.url
        except:
            return settings.DEFAULT_IMG

    def delete(self, *args, **kwargs):
        try:
            remove_thumbnails(self.img.path)
            remove_file(self.img.path)
        except:
            pass
        super(AbstractImg, self).delete(*args, **kwargs)

    def slide_thumbnail(self):
        if self.img:
            path = self.img.url
            tmb = make_thumbnail(path, width=60, height=60, aspect=1)
        else:
            tmb = '/static/img/icon-no.gif"'
            path = '/static/img/icon-no.gif"'
        return '<a target="_blank" href="%s"><img src="%s" /></a>' % (path, tmb)

    slide_thumbnail.allow_tags = True


@python_2_unicode_compatible
class Material(AbstractImg):
    name = std_text_field(_('Material'))

    class Meta:
        verbose_name = _("Material")
        verbose_name_plural = _("Materials")
        abstract = True

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class AbstractName(AbstractImg):
    name = models.CharField(verbose_name=_("Name"), max_length=255, blank=True, null=True, db_index=True)
    name_en = models.CharField(verbose_name=_("Name(English"), max_length=255, blank=True, null=True, db_index=True)
    enabled = models.BooleanField(verbose_name=_("Enabled in system"), default=True, db_index=True)
    description = models.TextField(verbose_name=_("Description"), blank=True, null=True)
    description_en = models.TextField(verbose_name=_("Description(English)"), blank=True, null=True)
    slug = models.CharField(verbose_name=_('URL-identifier'), max_length=100, blank=True, null=True, db_index=True)
    position = models.PositiveSmallIntegerField(verbose_name=_('Priority'), db_index=True, default=0,
                                                blank=True)
    order_in_list = models.IntegerField(_('Order in list'), default=0, db_index=True)
    docs = models.IntegerField(blank=True, null=True)
    pics = models.IntegerField(blank=True, null=True)
    views = models.IntegerField(blank=True, null=True)
    comments = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['-order_in_list', 'name']
        abstract = True

    def __str__(self):
        return self.name

    @property
    def get_name(self):
        try:
            if get_language() == 'en':
                if self.name_en:
                    return self.name_en
            return self.name
        except:
            return self.name

    def get_description(self):
        try:
            if get_language() == 'en':
                if self.description_en:
                    return self.description_en
        except:
            pass
        return self.description

    @property
    def main_image(self):
        try:
            return self.allpics[0].pic.url
        except:
            return settings.DEFAULT_IMG

    @property
    def allpics(self):
        from nnmware.core.models import Pic

        return Pic.objects.for_object(self).order_by('-primary')

    def save(self, *args, **kwargs):
        if not self.slug:
            if not self.id:
                super(AbstractName, self).save(*args, **kwargs)
            self.slug = self.id
        else:
            self.slug = str(self.slug).strip().replace(' ', '-')
        super(AbstractName, self).save(*args, **kwargs)


@python_2_unicode_compatible
class AbstractColor(AbstractName):
    pass

    class Meta:
        verbose_name = _("Color")
        verbose_name_plural = _("Colors")
        abstract = True

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Tree(AbstractName):
    """
    Main nodes tree
    """
    parent = models.ForeignKey('self', verbose_name=_("Parent"), blank=True, null=True, related_name="children")
    ordering = models.IntegerField(_("Ordering"), default=0, help_text=_("Override alphabetical order in tree display"))
    rootnode = models.BooleanField(_('Root node'), default=False)
    login_required = models.BooleanField(verbose_name=_("Login required"), default=False, help_text=_(
        "Enable this if users must login before access with this objects."))
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_('Category Admins'),
                                    related_name='%(app_label)s_%(class)s_adm')

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
        return reverse(self.slug_detail,
                       kwargs={'parent_slugs': slug_list, 'slug': self.slug})

    def get_separator(self):
        return ' > '

    def _parents_repr(self):
        name_list = [node.name for node in self._recurse_for_parents(self)]
        return self.get_separator().join(name_list)

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
            return [catidlist[0].name, catidlist[0].ordering]
        return [self.name, self.ordering]

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
        if not isinstance(L, list):
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


@python_2_unicode_compatible
class AbstractContent(models.Model):
    # Generic Foreign Key Fields
    content_type = models.ForeignKey(ContentType, null=True, blank=True, related_name="%(class)s_cntype")
    object_id = models.PositiveIntegerField(_('object ID'), null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    primary = models.BooleanField(_('Is primary'), default=False)

    class Meta:
        abstract = True

    objects = AbstractContentManager()

    def __str__(self):
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
                             related_name="%(class)s_f_user")
    description = std_text_field(_("Description"))
    size = models.IntegerField(editable=False, null=True, blank=True)
    ordering = models.IntegerField(_("Ordering"), default=0, help_text=_("Override alphabetical order in list display"))
    locked = models.BooleanField(_('Is locked'), default=False)

    class Meta:
        abstract = True


class AbstractIP(models.Model):
    ip = models.IPAddressField(verbose_name=_('IP'), null=True, blank=True)
    user_agent = models.CharField(verbose_name=_('User Agent'), null=True, blank=True, max_length=255)

    class Meta:
        abstract = True


class AbstractContact(AbstractImg):
    mobile_personal = std_text_field(_('Personal mobile phone'), max_length=12)
    mobile_work = std_text_field(_('Work mobile phone '), max_length=12)
    landline_personal = std_text_field(_('Personal landline phone'), max_length=12)
    landline_work = std_text_field(_('Work landline phone'), max_length=12)
    icq = std_text_field(_('ICQ'), max_length=30)
    skype = std_text_field(_('Skype'), max_length=30)
    jabber = std_text_field(_('Jabber'), max_length=50)
    publicmail = std_email_field(_('Public email'))
    privatemail = std_email_field(_('Private email'))
    website = std_url_field(_('Website'))
    personal_website = std_url_field(_('Personal Website'))
    facebook = std_url_field(_('Facebook'))
    googleplus = std_url_field(_('Google+'))
    twitter = std_url_field(_('Twitter'))
    vkontakte = std_url_field(_('VKontakte'))
    odnoklassniki = std_url_field(_('Odnoklassniki'))
    moikrug = std_url_field(_('Moi krug'))
    other_social = std_url_field(_('Other social networks'))
    hide_mobile_personal = models.BooleanField(_('Hide personal mobile phone'), default=False)
    hide_mobile_work = models.BooleanField(_('Hide work mobile phone'), default=False)
    hide_landline_personal = models.BooleanField(_('Hide personal landline phone'), default=False)
    hide_landline_work = models.BooleanField(_('Hide work landline phone'), default=False)
    hide_icq = models.BooleanField(_('Hide icq'), default=False)
    hide_skype = models.BooleanField(_('Hide skype'), default=False)
    hide_jabber = models.BooleanField(_('Hide jabber'), default=False)
    hide_publicmail = models.BooleanField(_('Hide publicmail'), default=False)
    hide_privatemail = models.BooleanField(_('Hide privatemail'), default=False)
    hide_website = models.BooleanField(_('Hide website'), default=False)
    hide_personal_website = models.BooleanField(_('Hide personal website'), default=False)
    hide_facebook = models.BooleanField(_('Hide facebook'), default=False)
    hide_googleplus = models.BooleanField(_('Hide googleplus'), default=False)
    hide_twitter = models.BooleanField(_('Hide twitter'), default=False)
    hide_vkontakte = models.BooleanField(_('Hide vkontakte'), default=False)
    hide_moikrug = models.BooleanField(_('Hide moikrug'), default=False)
    hide_odnoklassniki = models.BooleanField(_('Hide odnoklassniki'), default=False)
    hide_other_social = models.BooleanField(_('Hide other social networks'), default=False)
    hide_address = models.BooleanField(_('Hide address'), default=False)

    class Meta:
        verbose_name = _("Contacts data")
        verbose_name_plural = _("Contact data")
        abstract = True


@python_2_unicode_compatible
class AbstractOrder(AbstractImg):
    order_in_list = models.IntegerField(_('Order in list'), default=0)
    name_en = std_text_field(_('English name'))

    class Meta:
        ordering = ['-order_in_list', ]
        abstract = True
        ordering = ['name', ]

    def __str__(self):
        return "%s" % self.name


SKILL_UNKNOWN = 0
SKILL_FAN = 1
SKILL_PRO = 2

SKILL_CHOICES = (
    (SKILL_UNKNOWN, _("Unknown")),
    (SKILL_FAN, _("Fan")),
    (SKILL_PRO, _("Pro")),
)


@python_2_unicode_compatible
class AbstractSkill(AbstractOrder):
    level = models.IntegerField(_('Level'), choices=SKILL_CHOICES, blank=True, null=True, default=SKILL_UNKNOWN)

    class Meta:
        abstract = True

    def __str__(self):
        return "%s :: %s " % (self.skill.name, self.get_level_display())


@python_2_unicode_compatible
class AbstractNnmwareProfile(AbstractDate, AbstractImg):
    main = models.BooleanField(_('Main profile'), default=False)
    first_name = std_text_field(_('First Name'), max_length=50)
    middle_name = std_text_field(_('Middle Name'), max_length=50)
    last_name = std_text_field(_('Last Name'), max_length=50)
    viewcount = models.PositiveIntegerField(default=0, editable=False)
    enabled = models.BooleanField(verbose_name=_("Enabled in system"), default=True)
    birthdate = models.DateField(verbose_name=_('Date birth'), blank=True, null=True)
    gender = models.CharField(_("Gender"), max_length=1, choices=GENDER_CHOICES, blank=True)
    is_employer = models.BooleanField(verbose_name=_("Account is employer"), default=False)
    is_public = models.BooleanField(verbose_name=_("Account is public"), default=False)

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

    @permalink
    def get_absolute_url(self):
        return "employer_view", (), {'pk': self.pk}

    @property
    def main_image(self):
        try:
            return self.allpics[0].pic.url
        except:
            return settings.DEFAULT_IMG

    @property
    def allpics(self):
        from nnmware.core.models import Pic
        return Pic.objects.for_object(self).order_by('-primary')


class PicsMixin(object):

    @property
    def main_image(self):
        try:
            return self.allpics[0].pic.url
        except:
            return settings.DEFAULT_IMG

    @property
    def allpics(self):
        from nnmware.core.models import Pic
        return Pic.objects.for_object(self).order_by('-primary')


class AbstractOffer(AbstractImg):
    created_date = models.DateTimeField(_("Created date"), default=now)
    start_date = models.DateTimeField(_("Start date"), default=now)
    end_date = models.DateTimeField(_("End date"), default=now)
    title = std_text_field(_('Title'))
    text = models.TextField(verbose_name=_("Offer text"), null=True, blank=True)
    enabled = models.BooleanField(verbose_name=_("Enabled"), default=False)
    slug = models.CharField(verbose_name=_('URL-identifier'), max_length=100, blank=True, null=True)
    order_in_list = models.IntegerField(_('Order in list'), default=0)

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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'))

    class Meta:
        abstract = True

    @property
    def get_user_name(self):
        try:
            return self.user.get_name
        except:
            return self.user.username


@python_2_unicode_compatible
class AbstractVendor(models.Model):
    name = models.CharField(_("Name of vendor"), max_length=200)
    name_en = models.CharField(_("Name of vendor(english)"), max_length=200, null=True, blank=True)
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
