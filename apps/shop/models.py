from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from nnmware.core.models import Tree, MetaData, MetaName


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
