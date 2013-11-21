# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import permalink, Q
from django.template.defaultfilters import floatformat
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.address.models import Country, AbstractLocation, Region
from nnmware.apps.business.models import Company
from nnmware.apps.money.models import MoneyBase
from nnmware.core.abstract import Tree, AbstractName, AbstractContent, AbstractOffer, Material, AbstractVendor
from nnmware.core.abstract import AbstractDate, AbstractColor, Unit, Parameter, AbstractIP, AbstractImg
from nnmware.core.fields import std_text_field
from nnmware.core.managers import ProductManager, ServiceManager
from django.utils.encoding import python_2_unicode_compatible
from nnmware.apps.money.models import AbstractDeliveryMethod
from nnmware.core.abstract import AbstractTeaser


class ProductCategory(Tree):
    slug_detail = 'product_category'

    class Meta:
        ordering = ['parent__id', ]
        verbose_name = _('Product Category')
        verbose_name_plural = _('Product Categories')

    @property
    def _active_set(self):
        return Product.objects.active().filter(category=self)


class ProductColor(AbstractColor):
    pass


class ProductMaterial(Material):
    pass


class Vendor(AbstractVendor):
    country = models.ForeignKey(Country, verbose_name=_('Country'), null=True, blank=True,
                                on_delete=models.SET_NULL)


class CargoService(Vendor):
    pass

    class Meta:
        verbose_name = _("Cargo Service")
        verbose_name_plural = _("Cargo Services")


class Product(AbstractName, MoneyBase, AbstractDate, AbstractTeaser):
    category = models.ForeignKey(ProductCategory, verbose_name=_('Category'), null=True, blank=True,
                                 on_delete=models.SET_NULL, related_name='shopcat')
    quantity = models.IntegerField(_('Quantity'), default=0, blank=True)
    colors = models.ManyToManyField(ProductColor, verbose_name=_('Colors'), null=True, blank=True)
    materials = models.ManyToManyField(ProductMaterial, verbose_name=_('Materials'), null=True, blank=True)
    related_products = models.ManyToManyField('self', verbose_name=_('Related products'), null=True, blank=True)
    shop_pn = models.CharField(max_length=100, verbose_name=_('Shop part number'), blank=True)
    vendor_pn = models.CharField(max_length=100, verbose_name=_('Vendor part number'), blank=True)
    vendor = models.ForeignKey(Vendor, verbose_name=_('Vendor'), null=True, blank=True,
                               on_delete=models.SET_NULL)
    avail = models.BooleanField(verbose_name=_("Available for order"), default=False)
    latest = models.BooleanField(verbose_name=_("Latest product"), default=False)
    bestseller = models.BooleanField(verbose_name=_("Bestseller"), default=False)
    discount = models.BooleanField(verbose_name=_("Discount"), default=False)
    on_main = models.BooleanField(verbose_name=_("On main page"), default=False)
    visible = models.BooleanField(verbose_name=_("Visible"), default=True)
    special_offer = models.BooleanField(verbose_name=_("Special offer"), default=False)
    discount_percent = models.DecimalField(verbose_name=_('Percent of discount'), blank=True, null=True,
                                           decimal_places=1, max_digits=4, default=0)
    width = models.IntegerField(_('Width, sm'), default=0, blank=True)
    height = models.IntegerField(_('Height, sm'), default=0, blank=True)
    depth = models.IntegerField(_('Depth, sm'), default=0, blank=True)
    weight = models.DecimalField(verbose_name=_('Weight, kg'), default=0, blank=True, decimal_places=3, max_digits=20)
    maincat = std_text_field(_('Main category'))
    maincatid = models.IntegerField(_('Main category id'), default=0, blank=True)
    region = models.ForeignKey(Region, verbose_name=_('Region'), blank=True, null=True, related_name="%(class)s_reg")
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_('Product Admins'),
                                    null=True, blank=True, related_name='%(class)s_adm')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), blank=True, null=True)
    company = models.ForeignKey(Company, verbose_name=_('Company'), blank=True, null=True, on_delete=models.SET_NULL)

    objects = ProductManager()

    class Meta:
    #        ordering = ['category__name','order_in_list','name']
        ordering = ['-created_date']
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def parameters(self):
        return ProductParameterValue.objects.for_object(self)

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
        return self.fullmoney / (now() - self.created_date).days

    @property
    def allorders(self):
        allitems = OrderItem.objects.filter(product_origin=self).values_list('order__pk', flat=True)
        return Order.objects.active().filter(pk__in=allitems).dates('created_date', 'day')

    @property
    def with_discount(self):
        if self.discount_percent > 0:
            result = self.amount * (100 - self.discount_percent) / 100
        else:
            result = self.amount
        return floatformat(result, 0)

    def save(self, *args, **kwargs):
        if self.slug is not None:
            self.maincat = self.category.get_root_catid()[0]
            self.maincatid = self.category.get_root_catid()[1]
        super(Product, self).save(*args, **kwargs)


class ParameterUnit(Unit):
    pass


@python_2_unicode_compatible
class ProductParameterCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Category of parameter'))

    class Meta:
        verbose_name = _("Category of product parameter")
        verbose_name_plural = _("Categories of product parameters")

    def __str__(self):
        return self.name


class ProductParameter(Parameter):
    category = models.ForeignKey(ProductParameterCategory, verbose_name=_('Category'), related_name='category',
                                 null=True, blank=True)
    unit = models.ForeignKey(ParameterUnit, verbose_name=_('Unit'), related_name='unit', null=True, blank=True)

    class Meta:
        verbose_name = _("Product parameter")
        verbose_name_plural = _("Product parameters")


@python_2_unicode_compatible
class ProductParameterValue(AbstractContent):
    parameter = models.ForeignKey(ProductParameter, verbose_name=_('Parameter'), related_name='parameter')
    value = std_text_field(_('Value of parameter'))
    order_in_list = models.IntegerField(_('Order in list'), default=0)
    keyparam = models.BooleanField(verbose_name=_("In key params"), default=False)

    class Meta:
        verbose_name = _("Product parameter value")
        verbose_name_plural = _("Product parameters values")

    def __str__(self):
        try:
            return "%s: %s %s" % (self.parameter.name, self.value, self.parameter.unit.name)
        except:
            return "%s: %s" % (self.parameter.name, self.value)


@python_2_unicode_compatible
class Basket(AbstractDate):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), related_name='basket', blank=True,
                             null=True, on_delete=models.SET_NULL)
    quantity = models.IntegerField(verbose_name=_('Quantity'))
    product = models.ForeignKey(Product, verbose_name=_('Product'), related_name='basket')
    session_key = models.CharField(max_length=40, verbose_name=_('Session key'), blank=True)
    addon = std_text_field(_('Add-on text'))

    class Meta:
        verbose_name = _("Basket")
        verbose_name_plural = _("Baskets")

    @property
    def sum(self):
        return self.quantity * int(self.product.with_discount)

    def __str__(self):
        try:
            return "%s" % self.user.username
        except:
            return "%s" % self.pk


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
        return self.filter(
            Q(status=STATUS_PROCESS) | Q(status=STATUS_SENT) | Q(status=STATUS_CLOSED) | Q(status=STATUS_SHIPPING) | Q(
                status=STATUS_WAIT))


class DeliveryMethod(AbstractDeliveryMethod):
    pass


@python_2_unicode_compatible
class Order(AbstractDate, AbstractIP):
    """
    Definition of orders.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), related_name='orders', blank=True,
                             null=True, on_delete=models.SET_NULL)
    comment = models.TextField(verbose_name=_('Shipping comment'), default='', blank=True)
    status = models.IntegerField(verbose_name=_('Status'), max_length=2, default=STATUS_UNKNOWN, choices=STATUS_ORDER)
    delivery = models.ForeignKey(DeliveryMethod, verbose_name=_('Delivery method'), blank=True,
                                 null=True, on_delete=models.SET_NULL)
    address = std_text_field(_('Shipping address'))
    tracknumber = std_text_field(_('Track number'))
    cargoservice = models.ForeignKey(CargoService, verbose_name=_('Cargo service'),
                                     related_name='cargo', null=True, blank=True)
    first_name = std_text_field(_('First Name'))
    middle_name = std_text_field(_('Middle Name'))
    last_name = std_text_field(_('Last Name'))
    lite = models.BooleanField(verbose_name=_("Not register shop user"), default=True)
    phone = std_text_field(_('Phone'))
    email = models.EmailField(_('Email'), blank=True)
    buyer_comment = std_text_field(_('Buyer comment'))
    seller_comment = std_text_field(_('Seller comment'))
    session_key = models.CharField(max_length=40, verbose_name=_('Session key'), blank=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Seller'), blank=True, null=True)

    objects = OrdersManager()

    class Meta:
        ordering = ['-created_date']
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    def __str__(self):
        return "%s" % self.pk

    @property
    def fullamount(self):
        result = 0
        for i in self.orderitem_set.all():
            result += i.fullamount
        return result

    @permalink
    def get_absolute_url(self):
        return "order_view", (), {'pk': self.pk}

    @permalink
    def get_complete_url(self):
        return "order_complete", (), {'pk': self.pk}

    @property
    def receiver(self):
        result = ''
        if self.last_name != '' and self.last_name is not None:
            result += self.last_name
        if self.first_name != '' and self.first_name is not None:
            result += ' ' + self.first_name
        if self.middle_name != '' and self.middle_name is not None:
            result += ' ' + self.middle_name
        return result

    @property
    def fio(self):
        result = ''
        if self.last_name != '' and self.last_name is not None:
            result += self.last_name.split(' ')[0]
        if self.first_name != '' and self.first_name is not None:
            result += ' ' + self.first_name[0]
        if self.middle_name != '' and self.middle_name is not None:
            result += ' ' + self.middle_name[0]
        return result


@python_2_unicode_compatible
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
    addon = std_text_field(_('Add-on text'))
    is_delivery = models.BooleanField(verbose_name=_("Delivery flag"), default=False)

    def __str__(self):
        return self.product_name

    @property
    def fullamount(self):
        return self.quantity * self.amount


@python_2_unicode_compatible
class DeliveryAddress(AbstractLocation):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), related_name='deliveryaddr')
    first_name = std_text_field(_('First Name'))
    middle_name = std_text_field(_('Middle Name'))
    last_name = std_text_field(_('Last Name'))
    phone = models.CharField(max_length=20, verbose_name=_('Phone'), default='', blank=True)
    skype = models.CharField(max_length=50, verbose_name=_('Skype'), default='', blank=True)

    class Meta:
        verbose_name = _("Delivery Address")
        verbose_name_plural = _("Delivery Addresses")

    def __str__(self):
        result = ''
        if self.zipcode != '' and self.zipcode is not None:
            result += self.zipcode
        if self.country is not None:
            result += ', ' + self.country.name
        if self.region is not None:
            result += _(', region ') + self.region.name
        if self.city is not None:
            result += _(', city ') + self.city.name
        if self.street != '' and self.street is not None:
            result += _(', street ') + ' ' + self.street
        if self.house_number != '' and self.house_number is not None:
            result += _(', house ') + self.house_number
        if self.building != '' and self.building is not None:
            result += _(', building ') + self.building
        if self.flat_number != '' and self.flat_number is not None:
            result += _(', flat ') + self.flat_number
        if self.last_name != '' and self.last_name is not None:
            result += ', ' + self.last_name
        if self.first_name != '' and self.first_name is not None:
            result += ' ' + self.first_name
        if self.middle_name != '' and self.middle_name is not None:
            result += ' ' + self.middle_name
        if self.phone != '' and self.phone is not None:
            result += _(', phone-') + self.phone
        if self.skype != '' and self.skype is not None:
            result += _(', skype-') + self.skype
        return result


@python_2_unicode_compatible
class Feedback(AbstractIP):
    created_date = models.DateTimeField(_("Created date"), default=now)
    name = std_text_field(_('Name'))
    email = std_text_field(_('Email'))
    message = models.TextField(verbose_name=_("Message"))
    answer = models.TextField(verbose_name=_("Answer"), blank=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Seller'), blank=True, null=True,
                               related_name='%(class)s_seller')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Buyer'), blank=True, null=True,
                              related_name='%(class)s_buyer')

    class Meta:
        ordering = ['-created_date']
        verbose_name = _('Feedback')
        verbose_name_plural = _('Feedback')

    def __str__(self):
        return "%s - %s" % (self.name, self.created_date)

    def get_absolute_url(self):
        return reverse('feedback_detail', args=[self.pk])


@python_2_unicode_compatible
class Review(AbstractIP, AbstractImg):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), related_name='reviews', null=True,
                             blank=True)
    created_date = models.DateTimeField(_("Created date"), default=now)
    name = std_text_field(_('Name'))
    w_position = std_text_field(_('Position'))
    message = models.TextField(verbose_name=_("Message"), blank=True, default='')
    visible = models.BooleanField(verbose_name=_("Visible"), default=False)
    vip = models.BooleanField(verbose_name=_("Vip"), default=False)

    class Meta:
        ordering = ['-created_date']
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')

    def __str__(self):
        return "%s - %s" % (self.name, self.created_date)


@python_2_unicode_compatible
class ShopText(AbstractTeaser):
    created_date = models.DateTimeField(_("Created date"), default=now)
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    content = models.TextField(verbose_name=_("Content"), blank=True)
    enabled = models.BooleanField(verbose_name=_("Enabled"), default=False)

    class Meta:
        ordering = ['-created_date']
        verbose_name = _('Shop text')
        verbose_name_plural = _('Shop texts')
        abstract = True

    def __str__(self):
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


class SpecialOffer(AbstractOffer):
    pass

    def save(self, *args, **kwargs):
        if not self.slug:
            if not self.pk:
                super(SpecialOffer, self).save(*args, **kwargs)
            self.slug = self.pk
        else:
            if SpecialOffer.objects.filter(slug=self.slug).exclude(pk=self.pk).count():
                self.slug = self.pk
        super(SpecialOffer, self).save(*args, **kwargs)

    @permalink
    def get_absolute_url(self):
        return "special_offer", (), {'pk': self.pk}


@python_2_unicode_compatible
class ShopCallback(AbstractIP):
    created_date = models.DateTimeField(_("Created date"), default=now)
    clientname = std_text_field(_('Client Name'))
    clientphone = std_text_field(_('Client Phone'))
    description = models.TextField(verbose_name=_("Description"), blank=True)
    closed = models.BooleanField(verbose_name=_("Closed"), default=False)
    quickorder = models.BooleanField(verbose_name=_("Quick order"), default=False)

    class Meta:
        ordering = ['-created_date']
        verbose_name = _('Shop Callback')
        verbose_name_plural = _('Shop Callbacks')

    def __str__(self):
        return "%s - %s" % (self.clientname, self.created_date)


@python_2_unicode_compatible
class ShopSlider(AbstractImg):
    visible = models.BooleanField(verbose_name=_("Visible"), default=False)
    slider_link = std_text_field(_('Slider_link'))

    class Meta:
        ordering = ['visible']
        verbose_name = _('ShopSlider')
        verbose_name_plural = _('ShopSliders')

    def __str__(self):
        return "Slider Image - %s" % self.pk


class ServiceCategory(Tree):
    slug_detail = 'service_category'

    class Meta:
        ordering = ['parent__id', ]
        verbose_name = _('Service Category')
        verbose_name_plural = _('Service Categories')

    @property
    def _active_set(self):
        return Service.objects.filter(category=self, visible=True)


class Service(AbstractName, MoneyBase, AbstractDate, AbstractTeaser):
    category = models.ForeignKey(ServiceCategory, verbose_name=_('Category'), null=True, blank=True,
                                 on_delete=models.SET_NULL, related_name='servicecat')
    related_services = models.ManyToManyField('self', verbose_name=_('Related services'), null=True, blank=True)
    shop_pn = models.CharField(max_length=100, verbose_name=_('Shop part number'), blank=True)
    vendor_pn = models.CharField(max_length=100, verbose_name=_('Vendor part number'), blank=True)
    avail = models.BooleanField(verbose_name=_("Available for order"), default=False)
    latest = models.BooleanField(verbose_name=_("Latest product"), default=False)
    bestseller = models.BooleanField(verbose_name=_("Bestseller"), default=False)
    discount = models.BooleanField(verbose_name=_("Discount"), default=False)
    on_main = models.BooleanField(verbose_name=_("On main page"), default=False)
    visible = models.BooleanField(verbose_name=_("Visible"), default=True)
    special_offer = models.BooleanField(verbose_name=_("Special offer"), default=False)
    discount_percent = models.DecimalField(verbose_name=_('Percent of discount'), blank=True, null=True,
                                           decimal_places=1, max_digits=4, default=0)
    region = models.ForeignKey(Region, verbose_name=_('Region'), blank=True, null=True, related_name="%(class)s_reg")
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_('Service Admins'),
                                    null=True, blank=True, related_name='%(class)s_adm')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), blank=True, null=True)
    company = models.ForeignKey(Company, verbose_name=_('Company'), blank=True, null=True, on_delete=models.SET_NULL)

    objects = ServiceManager()

    class Meta:
        ordering = ['-created_date']
        verbose_name = _("Service")
        verbose_name_plural = _("Services")

    @permalink
    def get_absolute_url(self):
        return "service_detail", (), {'pk': self.pk}
