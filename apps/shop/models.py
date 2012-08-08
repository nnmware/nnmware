from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from nnmware.core.models import Tree, MetaName, MetaContent
from nnmware.core.models import Unit


class ProductCategory(Tree):
    slug_detail = 'product_category'

    class Meta:
        ordering = ['parent__id',]
        verbose_name = _('Product Category')
        verbose_name_plural = _('Product Categories')


class Product(MetaName):
    category = models.ForeignKey(ProductCategory, verbose_name=_('Category'), null=True, blank=True,
        on_delete=models.SET_NULL)
    created_date = models.DateTimeField(_("Created date"), default=datetime.now())
    updated_date = models.DateTimeField(_("Updated date"), null=True, blank=True)

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

class ParameterUnit(Unit):
    pass

class ProductParameter(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name of parameter'))
    unit = models.ForeignKey(ParameterUnit, verbose_name=_('Unit'), related_name='unit')
    is_string = models.BooleanField(_('Is string?'), default=True)

    class Meta:
        verbose_name = _("Product parameter")
        verbose_name_plural = _("Product parameters")

    def __unicode__(self):
        return "%s" % self.name

class ProductParameterValue(MetaContent):
    parameter = models.ForeignKey(ProductParameter, verbose_name=_('Parameter'), related_name='parameter')
    string_value = models.CharField(max_length=255, verbose_name=_('String value of parameter'), blank=True)
    number_value = models.DecimalField(verbose_name=_('Number value of parameter'), default=0, decimal_places=1, max_digits=4)

    class Meta:
        verbose_name = _("Product parameter value")
        verbose_name_plural = _("Product parameters values")

    def __unicode__(self):
        return "%s = %s %s" % self.parameter.name, self.value, self.parameter.unit.name

    @property
    def value(self):
        if self.parameter.is_string:
            return self.string_value
        else:
            return self.number_value



