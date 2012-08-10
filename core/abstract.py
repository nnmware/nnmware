# -*- coding: utf-8 -*-
# Base abstract classed nnmware(c)2012

from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

class Color(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Color'))

    class Meta:
        verbose_name = _("Color")
        verbose_name_plural = _("Colors")
        abstract = True

    def __unicode__(self):
        return self.name

class MetaDate(models.Model):
    created_date = models.DateTimeField(_("Created date"), default=datetime.now())
    updated_date = models.DateTimeField(_("Updated date"), null=True, blank=True)

    class Meta:
        abstract = True
