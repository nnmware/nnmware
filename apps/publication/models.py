# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from nnmware.core.models import LikeMixin, ContentBlockMixin
from nnmware.apps.address.models import Region
from nnmware.core.abstract import Tree, AbstractDate, AbstractName
from nnmware.core.constants import STATUS_CHOICES, STATUS_UNKNOWN
from nnmware.core.managers import StatusManager


class PublicationCategory(Tree):
    slug_detail = 'publication_category'

    class Meta:
        ordering = ['parent__id', 'name']
        verbose_name = _('Publication Category')
        verbose_name_plural = _('Publication Categories')

    @property
    def obj_active_set(self):
        return Publication.objects.active().filter(category=self)


class Publication(AbstractDate, AbstractName, LikeMixin, ContentBlockMixin):
    region = models.ForeignKey(Region, verbose_name=_('Region'), blank=True, null=True, related_name="%(class)s_reg",
                               on_delete=models.PROTECT)
    category = models.ForeignKey(PublicationCategory, verbose_name=_('Category'), null=True, blank=True,
                                 on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), on_delete=models.PROTECT)
    status = models.IntegerField(_("Status"), choices=STATUS_CHOICES, default=STATUS_UNKNOWN)

    objects = StatusManager()

    class Meta:
        ordering = ['-created_date', ]
        verbose_name = _('Publication')
        verbose_name_plural = _('Publications')

    def get_absolute_url(self):
        return reverse('publication_detail', args=[self.pk])

    def get_edit_url(self):
        return reverse('publication_edit', args=[self.pk])
