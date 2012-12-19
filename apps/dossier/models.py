# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models
from nnmware.apps.address.models import Institution
from django.utils.translation import ugettext_lazy as _
from nnmware.core.models import tuplify, current_year

EDUCATION_END = map(tuplify, range(current_year-55, current_year+1))


class Education(models.Model):
    institution = models.ForeignKey(Institution, verbose_name=_('Institution'),
        related_name='edu', blank=True, null=True)
    education_end = models.IntegerField(verbose_name=_('End of education'), choices=EDUCATION_END,
        default=current_year)
    master_course = models.CharField(max_length=50,verbose_name=_('Master of course'), blank=True,default='')
    diploma_work = models.CharField(max_length=50, verbose_name=_('Diploma work'), blank=True, default='')
    diploma_role = models.CharField(max_length=50, verbose_name=_('Role'), blank=True, default='')
    specialty = models.CharField(max_length=50, verbose_name=_('Specialty'), blank=True, default='')

    class Meta:
        verbose_name = _("Education")
        verbose_name_plural = _("Educations")

