# -*- coding: utf-8 -*-
from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.address.models import Country, City, Region
from nnmware.apps.money.models import MoneyBase
from nnmware.core.abstract import Tree, MetaName, MetaContent
from nnmware.core.abstract import MetaDate, Color, Unit, Parameter


class ProductCategory(Tree):
    slug_detail = 'product_category'

    class Meta:
        ordering = ['parent__id',]
        verbose_name = _('Product Category')
        verbose_name_plural = _('Product Categories')

class ProductColor(Color):
    pass

class Vendor(models.Model):
    name = models.CharField(_("Name of vendor"),max_length=200)
    website = models.URLField(_("URL"), blank=True)
    description = models.TextField(_("Description of Vendor"), help_text=_("Description of Vendor"), default='', blank=True)
    country = models.ForeignKey(Country, verbose_name=_('Country'), null=True, blank=True,
        on_delete=models.SET_NULL)

    class Meta:
        ordering = ['name', 'website']
        verbose_name = _("Vendor")
        verbose_name_plural = _("Vendors")

    def __unicode__(self):
        return self.name


class Product(MetaName, MoneyBase, MetaDate):
    category = models.ForeignKey(ProductCategory, verbose_name=_('Category'), null=True, blank=True,
        on_delete=models.SET_NULL)
    quantity = models.IntegerField(_('Quantity'), default=0, blank=True)
    color = models.ForeignKey(ProductColor, verbose_name=_('Color'), null=True, blank=True,
        on_delete=models.SET_NULL)
    shop_pn = models.CharField(max_length=100, verbose_name=_('Shop part number'), blank=True)
    vendor_pn = models.CharField(max_length=100, verbose_name=_('Vendor part number'), blank=True)
    vendor = models.ForeignKey(Vendor, verbose_name=_('Vendor'), null=True, blank=True,
        on_delete=models.SET_NULL)
    avail = models.BooleanField(verbose_name=_("Available for order"), default=False)
    latest = models.BooleanField(verbose_name=_("Latest product"), default=False)
    teaser = models.TextField(verbose_name=_("Teaser"), blank=True, null=True)

    class Meta:
        ordering = ['category__name','order_in_list','name']
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def parameters(self):
        return ProductParameterValue.objects.metalinks_for_object(self)

    @permalink
    def get_absolute_url(self):
        return "product_detail", (), {'pk': self.pk}

class ParameterUnit(Unit):
    pass

class ProductParameterCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Category of parameter'))

    class Meta:
        verbose_name = _("Category of product parameter")
        verbose_name_plural = _("Categories of product parameters")

    def __unicode__(self):
        return self.name

class ProductParameter(Parameter):
    category = models.ForeignKey(ProductParameterCategory, verbose_name=_('Category'), related_name='category', null=True, blank=True)
    unit = models.ForeignKey(ParameterUnit, verbose_name=_('Unit'), related_name='unit', null=True, blank=True)

    class Meta:
        verbose_name = _("Product parameter")
        verbose_name_plural = _("Product parameters")

class ProductParameterValue(MetaContent):
    parameter = models.ForeignKey(ProductParameter, verbose_name=_('Parameter'), related_name='parameter')
    value = models.CharField(max_length=255, verbose_name=_('Value of parameter'), blank=True)
    order_in_list = models.IntegerField(_('Order in list'), default=0)
    keyparam = models.BooleanField(verbose_name=_("In key params"), default=False)

    class Meta:
        verbose_name = _("Product parameter value")
        verbose_name_plural = _("Product parameters values")

    def __unicode__(self):
        try:
            return "%s: %s %s" % (self.parameter.name, self.value, self.parameter.unit.name)
        except :
            return "%s: %s" % (self.parameter.name, self.value)


class Basket(MetaDate):
    user = models.ForeignKey(User, verbose_name=_('User'), related_name='basket',blank=True, null=True)
    quantity = models.IntegerField(verbose_name=_('Quantity'))
    product = models.ForeignKey(Product, verbose_name=_('Product'), related_name='basket')
    session_key = models.CharField(max_length=40, verbose_name=_('Session key'), blank=True)

    class Meta:
        verbose_name = _("Basket")
        verbose_name_plural = _("Baskets")

    @property
    def sum(self):
        return self.quantity*self.product.amount

STATUS_UNKNOWN = 0
STATUS_WAIT = 1
STATUS_PROCESS = 2
STATUS_SENT = 3
STATUS_CANCEL = 4
STATUS_CLOSED = 5
STATUS_UNDO = 6
STATUS_SHIPPING = 7

STATUS_ORDER = (
        (STATUS_UNKNOWN, _('Unknown')),
        (STATUS_WAIT, _('Wait')),
        (STATUS_PROCESS, _('Process')),
        (STATUS_SENT, _('Sent')),
        (STATUS_CANCEL, _('Cancel')),
        (STATUS_CLOSED, _('Closed')),
        (STATUS_UNDO, _('Undo')),
        (STATUS_SHIPPING, _('Shipping')),
        )

class Order(MetaDate, MoneyBase):
    """
    Definition of orders.
    """
    user = models.ForeignKey(User, verbose_name=_('User'), related_name='user')
    name = models.CharField(verbose_name=_('Name'), max_length=80, blank=True, null=True)
    comment = models.TextField(verbose_name=_('Shipping comment'), blank=True, default='')
    status = models.IntegerField(verbose_name=_('Status'), max_length=2, default=0, choices=STATUS_ORDER)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    def __unicode__(self):
        if self.name <> '':
            return self.name
        else:
            return "%s" % self.pk

class OrderItem(MoneyBase):
    """
    Definition of order's details.
    """
    order = models.ForeignKey(Order)
    product = models.ForeignKey(Product, blank=True, null=True)
    product_name = models.CharField(verbose_name=_('Product Name'), max_length=250, blank=True, null=True)
    quantity = models.PositiveIntegerField(verbose_name=_('Quantity'))

    def __unicode__(self):
        try:
            return self.product.get_name
        except :
            return self.product_name

class DeliveryAddress(models.Model):
    user = models.ForeignKey(User, verbose_name=_('User'), related_name='user')
    country = models.ForeignKey(Country, verbose_name=_('Country'), blank=True)
    region = models.ForeignKey(Region, verbose_name=_('Region'), blank=True)
    zipcode = models.CharField(max_length=20,verbose_name=_('Zipcode'), blank=True )
    city = models.ForeignKey(City, verbose_name=_('City'))
    street = models.CharField(max_length=100, verbose_name=_('Street'), blank=True)
    house_number = models.IntegerField(_('Number of house'), blank=True, null=True)
    building = models.CharField(max_length=5,verbose_name=_('Building'), blank=True)
    flat_number = models.IntegerField(_('Number of flat'), blank=True, null=True)

    class Meta:
        verbose_name = _("Delivery Address")
        verbose_name_plural = _("Delivery Addresses")
