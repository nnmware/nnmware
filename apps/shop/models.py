from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
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

class Product(MetaName, MoneyBase):
    category = models.ForeignKey(ProductCategory, verbose_name=_('Category'), null=True, blank=True,
        on_delete=models.SET_NULL)
    created_date = models.DateTimeField(_("Created date"), default=datetime.now())
    updated_date = models.DateTimeField(_("Updated date"), null=True, blank=True)
    quantity = models.IntegerField(_('Quantity'), default=0, blank=True)
    color = models.ForeignKey(ProductColor, verbose_name=_('Color'), null=True, blank=True,
        on_delete=models.SET_NULL)


    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

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



