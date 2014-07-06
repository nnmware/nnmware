# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

STATUS_UNKNOWN = 0
STATUS_DELETE = 1
STATUS_LOCKED = 2
STATUS_PUBLISHED = 3
STATUS_STICKY = 4
STATUS_MODERATION = 5
STATUS_DRAFT = 6

STATUS_CHOICES = (
    (STATUS_UNKNOWN, _("Unknown")),
    (STATUS_DELETE, _("Deleted")),
    (STATUS_LOCKED, _("Locked")),
    (STATUS_PUBLISHED, _("Published")),
    (STATUS_STICKY, _("Sticky")),
    (STATUS_MODERATION, _("Moderation")),
    (STATUS_DRAFT, _("Draft")),
)


CONTENT_UNKNOWN = 0
CONTENT_TEXT = 1
CONTENT_IMAGE = 2
CONTENT_VIDEO = 3
CONTENT_CODE = 4
CONTENT_QUOTE = 5
CONTENT_URL = 6
CONTENT_RAW = 7


CONTENT_CHOICES = (
    (CONTENT_UNKNOWN, _("Unknown")),
    (CONTENT_TEXT, _("Text")),
    (CONTENT_IMAGE, _("Image")),
    (CONTENT_VIDEO, _("Video")),
    (CONTENT_CODE, _("Code")),
    (CONTENT_QUOTE, _("Quote")),
    (CONTENT_URL, _("Url")),
    (CONTENT_RAW, _("Raw input")),
)


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


GENDER_CHOICES = (('F', _('Female')), ('M', _('Male')), ('N', _('None')))
