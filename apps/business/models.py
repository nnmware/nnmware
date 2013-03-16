# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from nnmware.apps.dossier.models import Education
from nnmware.core.abstract import AbstractName, AbstractImg
from nnmware.core.fields import std_text_field
from django.utils.encoding import python_2_unicode_compatible
from nnmware.core.models import Pic


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


@python_2_unicode_compatible
class TypeEmployerProfile(AbstractName):
    employer_type = models.ForeignKey(TypeEmployer,verbose_name=_('Type of employer'))
    is_radio = models.BooleanField(verbose_name=_('Radio button?'), default=False)

    class Meta:
        verbose_name = _("Type of employer profile")
        verbose_name_plural = _("Types of employers profiles")

    def __str__(self):
        return "%s :: %s" % (self.employer_type.name, self.name)

@python_2_unicode_compatible
class TypeEmployerOther(AbstractName):
    employer_type = models.ForeignKey(TypeEmployer,verbose_name=_('Type of employer'))
    is_radio = models.BooleanField(verbose_name=_('Radio button?'), default=False)

    class Meta:
        verbose_name = _("Type of other sphere act. employer")
        verbose_name_plural = _("Types of other sphere act. employers")

    def __str__(self):
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
    employer_profile = models.ManyToManyField(TypeEmployerProfile, verbose_name=_('Types of employer profile'),blank=True, null=True)
    employer_other = models.ManyToManyField(TypeEmployerOther, verbose_name=_('Types of employer'),blank=True, null=True)

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


class Agency(AbstractName):

    class Meta:
        verbose_name = _("Agency")
        verbose_name_plural = _("Agencies")


class AbstractEmployee(AbstractImg):
    agent_name = std_text_field(_('Agent name'))
    agent_phone = models.CharField(max_length=20, verbose_name=_('Mobile phone of agent'), blank=True, default='')
    agent_email = models.EmailField(verbose_name=_('Agent Email'), blank=True, null=True)
    agent_avatar = models.ForeignKey(Pic, blank=True, null=True)
    agent_only = models.BooleanField(_('Contact only with agent'), default=False)
    permanent_work = std_text_field(_('Permanent place of work'))
    awards = std_text_field(_('Awards, achievements, titles'))
    payment_from = models.IntegerField(verbose_name=_('Amount payment from'),null=True, blank=True)
    payment_to = models.IntegerField(verbose_name=_('Amount payment to'),null=True, blank=True)
    additionally = models.TextField(verbose_name=_("Additionally"), blank=True, default='')
    source_about_resource = std_text_field(_('Source about our resource'))
    education = models.ManyToManyField(Education, verbose_name=_('Education'), blank=True, null=True)
    agency = models.ManyToManyField(Agency, verbose_name=_('In agency base'), blank=True, null=True)

    class Meta:
        verbose_name = _("Employee")
        verbose_name_plural = _("Employees")
        abstract = True

    @property
    def get_agent_avatar(self):
        try:
            return self.agent_avatar.pic.url
        except :
            return settings.DEFAULT_AVATAR

    def delete(self, *args, **kwargs):
        self.agent_avatar.delete()
        super(AbstractEmployee, self).delete(*args, **kwargs)
