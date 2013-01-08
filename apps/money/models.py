# -*- coding: utf-8 -*-

from datetime import datetime
from django.conf import settings
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.db import models
from nnmware.apps.address.models import Country
from nnmware.core.managers import FinancialManager
from nnmware.core.models import Doc
from django.utils.encoding import python_2_unicode_compatible

#---------------------------------------------------------------------------
@python_2_unicode_compatible
class Currency(models.Model):
    code = models.CharField(max_length=3, verbose_name=_('Currency code'))
    country = models.ForeignKey(Country, verbose_name=_('Country'), on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(verbose_name=_("Name"), max_length=100)
    name_en = models.CharField(verbose_name=_("Name(English"), max_length=100, blank=True)

    class Meta:
        unique_together = ('code',)
        verbose_name = _("Currency")
        verbose_name_plural = _("Currencies")

    def __str__(self):
        return "%s :: %s" % (self.code, self.name)

#---------------------------------------------------------------------------
@python_2_unicode_compatible
class ExchangeRate(models.Model):
    currency = models.ForeignKey(Currency, verbose_name=_('Currency'), on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(verbose_name=_('On date'))
    nominal = models.SmallIntegerField(verbose_name=_('Nominal'), default=1)
    official_rate = models.DecimalField(verbose_name=_('Official Rate'), default=0, max_digits=10, decimal_places=4)
    rate = models.DecimalField(verbose_name=_('Rate'), default=0, max_digits=10, decimal_places=4)


    class Meta:
        ordering = ("-date",'currency__code')
        unique_together = ('currency','date','rate')
        verbose_name = _("Exchange Rate")
        verbose_name_plural = _("Exchange Rates")

    def __str__(self):
        return "%s :: %s :: %s :: %s" % (self.currency, self.date, self.official_rate, self.rate)


#---------------------------------------------------------------------------
class MoneyBase(models.Model):
    amount = models.DecimalField(verbose_name=_('Amount'), default=0, max_digits=20, decimal_places=3)
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

#---------------------------------------------------------------------------
@python_2_unicode_compatible
class Transaction(MoneyBase):
    """
    Transaction(no more words)
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"))

    actor_ctype = models.ForeignKey(ContentType, verbose_name=_("Object Content Type"), null=True, blank=True,
        related_name='transaction_object', on_delete=models.SET_NULL)
    actor_oid = models.CharField(max_length=255, verbose_name=_("ID of object"), null=True, blank=True)
    actor = GenericForeignKey('actor_ctype', 'actor_oid')
    date = models.DateTimeField(verbose_name=_("Date"), default=datetime.now)
    status = models.IntegerField(_("Transaction status"), choices=TRANSACTION_STATUS, default=TRANSACTION_UNKNOWN)
    target_ctype = models.ForeignKey(ContentType, verbose_name=_("Target Content Type"), null=True, blank=True,
        related_name='transaction_target', on_delete=models.SET_NULL)
    target_oid = models.CharField(max_length=255, verbose_name=_("ID of target"), null=True, blank=True)
    target = GenericForeignKey('target_ctype', 'target_oid')

    objects = FinancialManager()

    class Meta:
        unique_together = ('user', 'actor_ctype', 'actor_oid', 'date', 'amount','currency')
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")

#    def __unicode__(self):
#        return '%s -> %s' % (self.user, self.date)

    def __str__(self):
        return _("User: %(user)s :: Date: %(date)s :: Object: %(actor)s :: Amount: %(amount)s %(currency)s") %\
                   { 'user': self.user.username,
                     'date': self.date,
                     'actor': self.actor,
                     'amount': self.amount,
                     'currency': self.currency}

#---------------------------------------------------------------------------
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


@python_2_unicode_compatible
class Bill(MoneyBase):
    """
    Financial account
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), blank=True, null=True)
    date = models.DateField(verbose_name=_("Date"), default=datetime.now())
    date_billed = models.DateField(verbose_name=_("Billed date"), default=datetime.now())
    status = models.IntegerField(_("Bill status"), choices=BILL_STATUS, default=BILL_UNKNOWN)
    target_ctype = models.ForeignKey(ContentType, verbose_name=_("Target Content Type"), null=True, blank=True,
        related_name='target_account_ctype', on_delete=models.SET_NULL)
    target_oid = models.CharField(max_length=255, verbose_name=_("ID of target"), null=True, blank=True)
    target = GenericForeignKey('target_ctype', 'target_oid')
    description = models.TextField(_("Description"), blank=True)

    objects = FinancialManager()

    class Meta:
        verbose_name = _("Bill")
        verbose_name_plural = _("Bills")

    def __str__(self):
        return _("User: %(user)s :: Date: %(date)s :: Target: %(target)s :: Amount: %(amount)s %(currency)s") %\
               { 'user': self.user,
                 'date': self.date,
                 'target': self.target,
                 'amount': self.amount,
                 'currency': self.currency}

    def docs(self):
        return Doc.objects.for_object(self)

