# -*- coding: utf-8 -*-
from datetime import datetime
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import permalink, Q, Count, Sum
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.address.models import Country, City, Region, AbstractLocation
from nnmware.apps.money.models import MoneyBase
from nnmware.core.abstract import Tree, AbstractName, AbstractContent
from nnmware.core.abstract import AbstractDate, Color, Unit, Parameter, AbstractIP
from nnmware.core.fields import std_url_field, std_text_field
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
    website = std_url_field(_("URL"))
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

class Product(AbstractName, MoneyBase, AbstractDate):
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
    bestseller = models.BooleanField(verbose_name=_("Bestseller"), default=False)
    discount = models.BooleanField(verbose_name=_("Discount"), default=False)
    visible = models.BooleanField(verbose_name=_("Visible"), default=True)

    objects = ProductManager()

    class Meta:
#        ordering = ['category__name','order_in_list','name']
        ordering = ['-created_date']
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def parameters(self):
        return ProductParameterValue.objects.metalinks_for_object(self)

    @permalink
    def get_absolute_url(self):
        return "product_detail", (), {'pk': self.pk}

    def allitems(self):
        active = Order.objects.active()
        return OrderItem.objects.filter(order__in=active, product_origin=self)

    @property
    def allcount(self):
        result = 0
        for item in self.allitems():
            result += item.quantity
        return result

    @property
    def fullmoney(self):
        result = 0
        for item in self.allitems():
            result += item.fullamount
        return result

    @property
    def effect(self):
        return self.fullmoney/(datetime.now()-self.created_date).days

    @property
    def allorders(self):
        items = self.allitems.values_list('order__pk',flat=True)
        return Order.objects.active.filter(pk__in=items).extra({'date_created' : "date(created_date)"}).values('date_created')

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

class ProductParameterValue(AbstractContent):
    parameter = models.ForeignKey(ProductParameter, verbose_name=_('Parameter'), related_name='parameter')
    value = std_text_field(_('Value of parameter'))
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


class Basket(AbstractDate):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), related_name='basket',blank=True, null=True)
    quantity = models.IntegerField(verbose_name=_('Quantity'))
    product = models.ForeignKey(Product, verbose_name=_('Product'), related_name='basket')
    session_key = models.CharField(max_length=40, verbose_name=_('Session key'), blank=True)

    class Meta:
        verbose_name = _("Basket")
        verbose_name_plural = _("Baskets")

    @property
    def sum(self):
        return self.quantity*self.product.amount

    def __unicode__(self):
        return "%s" % self.user.username


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

class OrdersManager(models.Manager):

    def active(self):
        return self.filter(Q(status=STATUS_PROCESS) | Q(status=STATUS_SENT)| Q(status=STATUS_CLOSED)| Q(status=STATUS_SHIPPING)| Q(status=STATUS_WAIT) )

class Order(AbstractDate):
    """
    Definition of orders.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), related_name='orders')
    comment = models.TextField(verbose_name=_('Shipping comment'), default='', blank=True)
    status = models.IntegerField(verbose_name=_('Status'), max_length=2, default=0, choices=STATUS_ORDER)
    address = models.CharField(verbose_name=_('Shipping address'), max_length=255)
    tracknumber = models.CharField(verbose_name=_('Track number'), max_length=100,default='', blank=True)
    cargoservice = models.ForeignKey(CargoService, verbose_name=_('Cargo service'),
        related_name='cargo', null=True, blank=True)
    first_name = std_text_field(_('First Name'))
    middle_name = std_text_field(_('Middle Name'))
    last_name = std_text_field(_('Last Name'))

    objects = OrdersManager()

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
    product_pn = std_text_field(_('Shop part number'))
    product_name = std_text_field(_('Product Name'))
    product_url = std_text_field(_('Product URL'))
    product_origin = models.ForeignKey(Product, null=True, blank=True)
    quantity = models.PositiveIntegerField(verbose_name=_('Quantity'))

    def __unicode__(self):
        return self.product_name

    @property
    def fullamount(self):
        return self.quantity*self.amount


class DeliveryAddress(AbstractLocation):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), related_name='deliveryaddr')
    region = models.ForeignKey(Region, verbose_name=_('Region'), blank=True, null=True)
    first_name = std_text_field(_('First Name'))
    middle_name = std_text_field(_('Middle Name'))
    last_name = std_text_field(_('Last Name'))
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
        if self.phone <> '' and self.phone is not None:
            result += _(', phone-') + self.phone
        if self.skype <> '' and self.skype is not None:
            result += _(', skype-') + self.skype
        return result

class Feedback(AbstractIP):
    created_date = models.DateTimeField(_("Created date"), default=datetime.now)
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    email = models.CharField(max_length=255, verbose_name=_('Email'))
    message = models.TextField(verbose_name=_("Message"))
    answer = models.TextField(verbose_name=_("Answer"), null=True, blank=True)

    class Meta:
        ordering = ['-created_date']
        verbose_name = _('Feedback')
        verbose_name_plural = _('Feedback')

    def __unicode__(self):
        return "%s - %s" % (self.name, self.created_date)

    def get_absolute_url(self):
        return reverse('feedback_detail', args=[self.pk])


class ShopText(models.Model):
    created_date = models.DateTimeField(_("Created date"), default=datetime.now)
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    teaser = models.TextField(verbose_name=_("Teaser"), null=True, blank=True)
    content = models.TextField(verbose_name=_("Content"), null=True, blank=True)
    enabled = models.BooleanField(verbose_name=_("Enabled"), default=False)

    class Meta:
        ordering = ['-created_date']
        verbose_name = _('Shop text')
        verbose_name_plural = _('Shop texts')
        abstract = True

    def __unicode__(self):
        return self.title


class ShopNews(ShopText):
    pass

    class Meta:
        verbose_name = _('Shop news')
        verbose_name_plural = _('Shop news')

class ShopArticle(ShopText):
    pass

    class Meta:
        verbose_name = _('Shop article')
        verbose_name_plural = _('Shop articles')

