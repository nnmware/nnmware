# -*- coding: utf-8 -*-
from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext as _
from nnmware.apps.address.models import Country, City, Region
from nnmware.apps.money.models import MoneyBase
from nnmware.core.abstract import Tree, MetaName, MetaContent
from nnmware.core.abstract import MetaDate, Color, Unit, Parameter, MetaIP
from nnmware.core.managers import ProductManager


class ProductCategory(Tree):
    slug_detail = 'product_category'

    class Meta:
        ordering = ['parent__id',]
        verbose_name = _('Product Category')
        verbose_name_plural = _('Product Categories')

    @property
    def _active_set(self):
        return Product.objects.active().filter(category=self)

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

class CargoService(Vendor):

    class Meta:
        ordering = ['name', 'website']
        verbose_name = _("Cargo Service")
        verbose_name_plural = _("Cargo Services")

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

    objects = ProductManager()
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

class Order(MetaDate):
    """
    Definition of orders.
    """
    user = models.ForeignKey(User, verbose_name=_('User'), related_name='orders')
    comment = models.TextField(verbose_name=_('Shipping comment'), default='', blank=True)
    status = models.IntegerField(verbose_name=_('Status'), max_length=2, default=0, choices=STATUS_ORDER)
    address = models.CharField(verbose_name=_('Shipping address'), max_length=255)
    tracknumber = models.CharField(verbose_name=_('Track number'), max_length=100,default='', blank=True)
    cargoservice = models.ForeignKey(CargoService, verbose_name=_('Cargo service'),
        related_name='cargo', null=True, blank=True)
    first_name = models.CharField(max_length=255, verbose_name=_('First Name'), default='',blank=True,null=True)
    middle_name = models.CharField(max_length=255, verbose_name=_('Middle Name'), default='',blank=True,null=True)
    last_name = models.CharField(max_length=255, verbose_name=_('Last Name'), default='',blank=True,null=True)


    class Meta:
        ordering = ['-created_date']
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    def __unicode__(self):
        return "%s" % self.pk

    @property
    def fullamount(self):
        result = 0
        for i in self.orderitem_set.all():
            result += i.fullamount
        return result

    @permalink
    def get_absolute_url(self):
        return "order_view", (), {'pk':self.pk}

    @property
    def receiver(self):
        result = ''
        if self.last_name <> '' and self.last_name is not None:
            result += self.last_name
        if self.first_name <> '' and self.first_name is not None:
            result += ' ' + self.first_name
        if self.middle_name <> '' and self.middle_name is not None:
            result += ' ' + self.middle_name
        return result


class OrderItem(MoneyBase):
    """
    Definition of order's details.
    """
    order = models.ForeignKey(Order)
    product_pn = models.CharField(verbose_name=_('Shop part number'), max_length=250, default='')
    product_name = models.CharField(verbose_name=_('Product Name'), max_length=250, default='')
    quantity = models.PositiveIntegerField(verbose_name=_('Quantity'))

    def __unicode__(self):
        return self.product_name

    @property
    def fullamount(self):
        return self.quantity*self.amount

class DeliveryAddress(models.Model):
    user = models.ForeignKey(User, verbose_name=_('User'), related_name='deliveryaddr')
    country = models.ForeignKey(Country, verbose_name=_('Country'), blank=True, null=True)
    region = models.ForeignKey(Region, verbose_name=_('Region'), blank=True, null=True)
    zipcode = models.CharField(max_length=20,verbose_name=_('Zipcode'), default='',blank=True,null=True)
    city = models.ForeignKey(City, verbose_name=_('City'), blank=True, null=True)
    street = models.CharField(max_length=100, verbose_name=_('Street'), default='',blank=True,null=True)
    house_number = models.CharField(max_length=5, verbose_name=_('Number of house'), default='',blank=True,null=True)
    building = models.CharField(max_length=25,verbose_name=_('Building'), default='',blank=True, null=True )
    flat_number = models.CharField(max_length=5, verbose_name=_('Number of flat'), default='',blank=True,null=True)
    first_name = models.CharField(max_length=255, verbose_name=_('First Name'), default='',blank=True,null=True)
    middle_name = models.CharField(max_length=255, verbose_name=_('Middle Name'), default='',blank=True,null=True)
    last_name = models.CharField(max_length=255, verbose_name=_('Last Name'), default='',blank=True,null=True)
    phone = models.CharField(max_length=20,verbose_name=_('Phone'), default='',blank=True,null=True)
    skype = models.CharField(max_length=50,verbose_name=_('Skype'), default='',blank=True,null=True)

    class Meta:
        verbose_name = _("Delivery Address")
        verbose_name_plural = _("Delivery Addresses")

    def __unicode__(self):
        result = ''
        if self.zipcode <> '' and self.zipcode is not None:
            result += self.zipcode
        if self.country is not None:
            result += ', ' + self.country.name
        if self.region is not None:
            result += _(', region ') + self.region.name
        if self.city is not None:
            result += _(', city ') + self.city.name
        if self.street <> '' and self.street is not None:
            result += _(', street ') +' '+ self.street
        if self.house_number <> '' and self.house_number is not None:
            result += _(', house ') + self.house_number
        if self.building <> '' and self.building is not None:
            result += _(', building ') + self.building
        if self.flat_number <> '' and self.flat_number is not None:
            result += _(', flat ') + self.flat_number
        if self.last_name <> '' and self.last_name is not None:
            result += ', ' + self.last_name
        if self.first_name <> '' and self.first_name is not None:
            result += ' ' + self.first_name
        if self.middle_name <> '' and self.middle_name is not None:
            result += ' ' + self.middle_name
        return result

class Feedback(MetaIP):
    created_date = models.DateTimeField(_("Created date"), default=datetime.now())
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    email = models.CharField(max_length=255, verbose_name=_('Email'))
    message = models.TextField(verbose_name=_("Message"))

    class Meta:
        ordering = ['-created_date']
        verbose_name = _('Feedback')
        verbose_name_plural = _('Feedback')

    def __unicode__(self):
        return "%s - %s" % (self.name, self.created_date)

class ShopNews(models.Model):
    created_date = models.DateTimeField(_("Created date"), default=datetime.now())
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    teaser = models.TextField(verbose_name=_("Teaser"), null=True, blank=True)
    content = models.TextField(verbose_name=_("Content"), null=True, blank=True)
    enabled = models.BooleanField(verbose_name=_("Enabled"), default=False)

    class Meta:
        ordering = ['-created_date']
        verbose_name = _('Shop news')
        verbose_name_plural = _('Shop news')

    def __unicode__(self):
        return self.title

