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
    (STATUS_UNKNOWN, _('Unknown')),
    (STATUS_DELETE, _('Deleted')),
    (STATUS_LOCKED, _('Locked')),
    (STATUS_PUBLISHED, _('Published')),
    (STATUS_STICKY, _('Sticky')),
    (STATUS_MODERATION, _('Moderation')),
    (STATUS_DRAFT, _('Draft')),
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
    (CONTENT_UNKNOWN, _('Unknown')),
    (CONTENT_TEXT, _('Text')),
    (CONTENT_IMAGE, _('Image')),
    (CONTENT_VIDEO, _('Video')),
    (CONTENT_CODE, _('Code')),
    (CONTENT_QUOTE, _('Quote')),
    (CONTENT_URL, _('Url')),
    (CONTENT_RAW, _('Raw input')),
)


NOTICE_UNKNOWN = 0
NOTICE_SYSTEM = 1
NOTICE_VIDEO = 2
NOTICE_TAG = 3
NOTICE_ACCOUNT = 4
NOTICE_PROFILE = 5

NOTICE_CHOICES = (
    (NOTICE_UNKNOWN, _('Unknown')),
    (NOTICE_SYSTEM, _('System')),
    (NOTICE_VIDEO, _('Video')),
    (NOTICE_TAG, _('Tag')),
    (NOTICE_ACCOUNT, _('Account')),
    (NOTICE_PROFILE, _('Profile')),
)


ACTION_UNKNOWN = 0
ACTION_SYSTEM = 1
ACTION_ADDED = 2
ACTION_COMMENTED = 3
ACTION_FOLLOWED = 4
ACTION_LIKED = 5

ACTION_CHOICES = (
    (ACTION_UNKNOWN, _('Unknown')),
    (ACTION_SYSTEM, _('System')),
    (ACTION_ADDED, _('Added')),
    (ACTION_COMMENTED, _('Commented')),
    (ACTION_FOLLOWED, _('Followed')),
    (ACTION_LIKED, _('Liked')),
)


GENDER_CHOICES = (('F', _('Female')), ('M', _('Male')), ('N', _('None')))


CONTACT_UNKNOWN = 0
CONTACT_MOBILE_PERSONAL = 1
CONTACT_MOBILE_WORK = 2
CONTACT_LANDLINE_PERSONAL = 3
CONTACT_LANDLINE_WORK = 4
CONTACT_MAIL_WORK = 5
CONTACT_MAIL_PERSONAL = 6
CONTACT_WEBSITE_WORK = 7
CONTACT_WEBSITE_PERSONAL = 8
CONTACT_ICQ = 9
CONTACT_SKYPE = 10
CONTACT_JABBER = 11
CONTACT_FACEBOOK = 12
CONTACT_GOOGLEPLUS = 13
CONTACT_VK = 14
CONTACT_ODNOKLASSNIKI = 15
CONTACT_TWITTER = 16
CONTACT_MOIKRUG = 17
CONTACT_GITHUB = 18
CONTACT_BITMESSAGE = 19
CONTACT_LINKEDIN = 20
CONTACT_TELEGRAM = 21
CONTACT_OTHER_SOCIAL = 99

CONTACTS_CHOICES = (
    (CONTACT_UNKNOWN, _('Unknown')),
    (CONTACT_MOBILE_PERSONAL, _('Personal mobile phone')),
    (CONTACT_MOBILE_WORK, _('Work mobile phone')),
    (CONTACT_LANDLINE_PERSONAL, _('Personal landline phone')),
    (CONTACT_LANDLINE_WORK, _('Work landline phone')),
    (CONTACT_MAIL_WORK, _('Public email')),
    (CONTACT_MAIL_PERSONAL, _('Private email')),
    (CONTACT_WEBSITE_WORK, _('Work website')),
    (CONTACT_WEBSITE_PERSONAL, _('Personal website')),
    (CONTACT_ICQ, _('ICQ')),
    (CONTACT_SKYPE, _('Skype')),
    (CONTACT_JABBER, _('Jabber')),
    (CONTACT_FACEBOOK, _('Facebook')),
    (CONTACT_GOOGLEPLUS, _('Google+')),
    (CONTACT_VK, _('VKontakte')),
    (CONTACT_ODNOKLASSNIKI, _('Odnoklassniki')),
    (CONTACT_TWITTER, _('Twitter')),
    (CONTACT_MOIKRUG, _('Moikrug')),
    (CONTACT_GITHUB, _('GitHub')),
    (CONTACT_BITMESSAGE, _('BitMessage')),
    (CONTACT_LINKEDIN, _('LinkedIn')),
    (CONTACT_TELEGRAM, _('Telegram')),
    (CONTACT_OTHER_SOCIAL, _('Other social network')),
)
