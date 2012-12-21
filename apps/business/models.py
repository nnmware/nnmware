# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from nnmware.core.abstract import AbstractName, AbstractImg
from nnmware.core.fields import std_text_field

class TypeEmployer(AbstractName):
    pass

    class Meta:
        ordering = ('-order_in_list','name')
        verbose_name = _("Type of employer")
        verbose_name_plural = _("Types of employers")

    @property
    def radio(self):
        return self.typeemployerprofile_set.filter(is_radio=True).order_by('-order_in_list','name')

    @property
    def multi(self):
        return self.typeemployerprofile_set.filter(is_radio=False).order_by('-order_in_list','name')


class TypeEmployerProfile(AbstractName):
    employer_type = models.ForeignKey(TypeEmployer,verbose_name=_('Type of employer'))
    is_radio = models.BooleanField(verbose_name=_('Radio button?'), default=False)

    class Meta:
        verbose_name = _("Type of employer profile")
        verbose_name_plural = _("Types of employers profiles")

    def __unicode__(self):
        return "%s :: %s" % (self.employer_type.name, self.name)

class TypeEmployerSphere(AbstractName):
    employer_type = models.ForeignKey(TypeEmployer,verbose_name=_('Type of employer'))

    class Meta:
        verbose_name = _("Type of sphere act. employer")
        verbose_name_plural = _("Types of sphere act. employers")

    def __unicode__(self):
        return "%s :: %s" % (self.employer_type.name, self.name)

class AbstractEmployer(AbstractImg):
    is_company = models.BooleanField(verbose_name=_('Employer is company'), default=False)
    name = std_text_field(_('Company name'))
    position = std_text_field(_('Work position'))
    description = models.TextField(verbose_name=_('Activities description '), blank=True, default='')
    work_on = models.TimeField(verbose_name=_('Work time from'),blank=True, null=True)
    work_off = models.TimeField(verbose_name=_('Work time to'),blank=True, null=True)
    phone_on = models.TimeField(verbose_name=_('Phone time from'),blank=True, null=True)
    phone_off = models.TimeField(verbose_name=_('Phone time to'),blank=True, null=True)
    employer_profile = models.ManyToManyField(TypeEmployerProfile,
        verbose_name=_('Types of employer profile'),blank=True, null=True)
    employer_profile_other = std_text_field(_('Other employer profile'))
    employer_type = models.ManyToManyField(TypeEmployer,
        verbose_name=_('Types of employer'),blank=True, null=True)
    employer_sphere_other = std_text_field(_('Other employer sphere'))

    class Meta:
        verbose_name = _("Employer")
        verbose_name_plural = _("Employers")
        abstract = True

    @property
    def emptypes(self):
        result = self.employer_profile.order_by('-order_in_list','name').values_list('employer_type',flat=True)
        return TypeEmployer.objects.filter(pk__in=result).values_list('pk',flat=True)

    @property
    def radio_profiles(self):
        return self.employer_profile.filter(is_radio=True)

