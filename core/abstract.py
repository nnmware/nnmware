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

class Unit(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name of unit'))

    class Meta:
        verbose_name = _("Unit")
        verbose_name_plural = _("Units")
        abstract = True

    def __unicode__(self):
        return "%s" % self.name

class Parameter(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name of parameter'))

    class Meta:
        verbose_name = _("Parameter")
        verbose_name_plural = _("Parameters")
        abstract = True

    def __unicode__(self):
        try:
            return "%s (%s)" % (self.name, self.unit.name)
        except :
            return "%s" % self.name

