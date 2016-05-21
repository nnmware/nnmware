# nnmware(c)2012-2016

from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.utils.timezone import now

from nnmware.core.abstract import Doc, AbstractContent
from nnmware.apps.address.models import Country
from nnmware.core.fields import std_text_field


class Currency(models.Model):
    code = models.CharField(max_length=3, verbose_name=_('Currency code'), db_index=True)
    country = models.ForeignKey(Country, verbose_name=_('Country'), on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(verbose_name=_("Name"), max_length=100, db_index=True)
    name_en = models.CharField(verbose_name=_("Name(English"), max_length=100, blank=True, db_index=True)

    class Meta:
        unique_together = ('code',)
        verbose_name = _("Currency")
        verbose_name_plural = _("Currencies")

    def __str__(self):
        return "%s :: %s" % (self.code, self.name)


class ExchangeRate(models.Model):
    currency = models.ForeignKey(Currency, verbose_name=_('Currency'), on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(verbose_name=_('On date'), db_index=True)
    nominal = models.SmallIntegerField(verbose_name=_('Nominal'), default=1, db_index=True)
    official_rate = models.DecimalField(verbose_name=_('Official Rate'), default=0, max_digits=10, decimal_places=4,
                                        db_index=True)
    rate = models.DecimalField(verbose_name=_('Rate'), default=0, max_digits=10, decimal_places=4, db_index=True)

    class Meta:
        ordering = ("-date", 'currency__code')
        unique_together = ('currency', 'date', 'rate')
        verbose_name = _("Exchange Rate")
        verbose_name_plural = _("Exchange Rates")

    def __str__(self):
        return "%s :: %s :: %s :: %s" % (self.currency, self.date, self.official_rate, self.rate)


class MoneyBase(models.Model):
    amount = models.DecimalField(verbose_name=_('Amount'), default=0, max_digits=22, decimal_places=5, db_index=True)
    currency = models.ForeignKey(Currency, verbose_name=_('Currency'), on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        abstract = True

TRANSACTION_UNKNOWN = 0
TRANSACTION_ACCEPTED = 1
TRANSACTION_COMPLETED = 2
TRANSACTION_CANCELED = 3

TRANSACTION_STATUS = (
    (TRANSACTION_UNKNOWN, _("Unknown")),
    (TRANSACTION_ACCEPTED, _("Accepted")),
    (TRANSACTION_COMPLETED, _("Completed")),
    (TRANSACTION_CANCELED, _("Cancelled")),
)


class Transaction(MoneyBase, AbstractContent):
    """
    Transaction(no more words)
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"))

    actor_ctype = models.ForeignKey(ContentType, verbose_name=_("Object Content Type"), null=True, blank=True,
                                    related_name='transaction_object', on_delete=models.SET_NULL)
    actor_oid = models.CharField(max_length=255, verbose_name=_("ID of object"), blank=True)
    actor = GenericForeignKey('actor_ctype', 'actor_oid')
    date = models.DateTimeField(verbose_name=_("Date"), default=now)
    status = models.IntegerField(_("Transaction status"), choices=TRANSACTION_STATUS, default=TRANSACTION_UNKNOWN)

    class Meta:
        unique_together = ('user', 'actor_ctype', 'actor_oid', 'date', 'amount', 'currency')
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")

    def __str__(self):
        return _("User: %(user)s :: Date: %(date)s :: Object: %(actor)s :: Amount: %(amount)s %(currency)s") % \
            {'user': self.user.username, 'date': self.date, 'actor': self.actor, 'amount': self.amount,
             'currency': self.currency}


BILL_UNKNOWN = 0
BILL_BILLED = 1
BILL_PAID = 2
BILL_CANCELED = 3

BILL_STATUS = (
    (BILL_UNKNOWN, _("Unknown")),
    (BILL_BILLED, _("Billed")),
    (BILL_PAID, _("Paid")),
    (BILL_CANCELED, _("Cancelled")),
)


class Bill(MoneyBase, AbstractContent):
    """
    Financial account
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), blank=True, null=True)
    date = models.DateField(verbose_name=_("Date"), default=now)
    date_billed = models.DateField(verbose_name=_("Billed date"), default=now)
    status = models.IntegerField(_("Bill status"), choices=BILL_STATUS, default=BILL_UNKNOWN)
    invoice_number = models.CharField(verbose_name=_("Invoice number"), max_length=255, blank=True, default='')
    description_small = models.CharField(verbose_name=_("Small description"), max_length=255, blank=True, default='')
    description = models.TextField(verbose_name=_("Description"), blank=True, default='')

    class Meta:
        verbose_name = _("Bill")
        verbose_name_plural = _("Bills")

    def __str__(self):
        return _("User: %(user)s :: Date: %(date)s :: Target: %(target)s :: Amount: %(amount)s %(currency)s") %\
            {'user': self.user, 'date': self.date, 'target': self.content_object, 'amount': self.amount,
             'currency': self.currency}

    def docs(self):
        return Doc.objects.for_object(self)


class AbstractDeliveryMethod(MoneyBase):
    name = std_text_field(_("Name of delivery method"))
    name_en = std_text_field(_("Name of delivery method(English)"))
    description = models.TextField(_("Description of delivery method"), default='', blank=True)
    description_en = models.TextField(_("Description of delivery method(English)"), default='', blank=True)
    enabled_for_registered = models.BooleanField(verbose_name=_("Enabled for registered users"), default=False)
    enabled_for_unregistered = models.BooleanField(verbose_name=_("Enabled for unregistered users"), default=False)
    position = models.PositiveSmallIntegerField(verbose_name=_('Priority'), db_index=True, default=0, blank=True)

    class Meta:
        verbose_name = _("Delivery method")
        verbose_name_plural = _("Delivery methods")
        abstract = True

    def __str__(self):
        return self.name
