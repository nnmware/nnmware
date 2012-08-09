# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.address.models import Country
from nnmware.apps.money.models import MoneyBase
from nnmware.core.models import Tree, MetaName, MetaContent, Color
from nnmware.core.models import Unit, Parameter


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


class Product(MetaName, MoneyBase):
    category = models.ForeignKey(ProductCategory, verbose_name=_('Category'), null=True, blank=True,
        on_delete=models.SET_NULL)
    created_date = models.DateTimeField(_("Created date"), default=datetime.now())
    updated_date = models.DateTimeField(_("Updated date"), null=True, blank=True)
    quantity = models.IntegerField(_('Quantity'), default=0, blank=True)
    color = models.ForeignKey(ProductColor, verbose_name=_('Color'), null=True, blank=True,
        on_delete=models.SET_NULL)
    shop_pn = models.CharField(max_length=100, verbose_name=_('Shop part number'), blank=True)
    vendor_pn = models.CharField(max_length=100, verbose_name=_('Vendor part number'), blank=True)
    vendor = models.ForeignKey(Vendor, verbose_name=_('Vendor'), null=True, blank=True,
        on_delete=models.SET_NULL)

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def parameters(self):
        return ProductParameterValue.objects.metalinks_for_object(self)

class ParameterUnit(Unit):
    pass


class ProductParameter(Parameter):
    unit = models.ForeignKey(ParameterUnit, verbose_name=_('Unit'), related_name='unit', null=True, blank=True)

    class Meta:
        verbose_name = _("Product parameter")
        verbose_name_plural = _("Product parameters")

class ProductParameterValue(MetaContent):
    parameter = models.ForeignKey(ProductParameter, verbose_name=_('Parameter'), related_name='parameter')
    value = models.CharField(max_length=255, verbose_name=_('Value of parameter'), blank=True)
    order_in_list = models.IntegerField(_('Order in list'), default=0)

    class Meta:
        verbose_name = _("Product parameter value")
        verbose_name_plural = _("Product parameters values")

    def __unicode__(self):
        try:
            return "%s: %s %s" % (self.parameter.name, self.value, self.parameter.unit.name)
        except :
            return "%s: %s" % (self.parameter.name, self.value)



