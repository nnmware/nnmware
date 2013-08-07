# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from django.db.models import permalink
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _, get_language
from nnmware.apps.address.models import AbstractLocation, MetaGeo
from nnmware.apps.dossier.models import Education
from nnmware.core.abstract import AbstractName, AbstractImg, Tree, AbstractDate, AbstractWorkTime, AbstractTeaser
from nnmware.core.fields import std_text_field
from django.utils.encoding import python_2_unicode_compatible
from nnmware.core.managers import CompanyManager, VacancyManager


class TypeEmployer(AbstractName):
    pass

    class Meta:
        ordering = ('-order_in_list', 'name')
        verbose_name = _("Type of employer")
        verbose_name_plural = _("Types of employers")

    @property
    def radio(self):
        return self.typeemployerprofile_set.filter(is_radio=True).order_by('-order_in_list', 'name')

    @property
    def multi(self):
        return self.typeemployerprofile_set.filter(is_radio=False).order_by('-order_in_list', 'name')

    @permalink
    def get_absolute_url(self):
        return 'employers_profile', (), {'slug': self.slug}


@python_2_unicode_compatible
class TypeEmployerProfile(AbstractName):
    employer_type = models.ForeignKey(TypeEmployer, verbose_name=_('Type of employer'))
    is_radio = models.BooleanField(verbose_name=_('Radio button?'), default=False)

    class Meta:
        verbose_name = _("Type of employer profile")
        verbose_name_plural = _("Types of employers profiles")

    def __str__(self):
        return "%s :: %s" % (self.employer_type.name, self.name)

    @permalink
    def get_absolute_url(self):
        return 'employers_group', (), {'slug': self.slug}


@python_2_unicode_compatible
class TypeEmployerOther(AbstractName):
    employer_type = models.ForeignKey(TypeEmployer, verbose_name=_('Type of employer'))
    is_radio = models.BooleanField(verbose_name=_('Radio button?'), default=False)

    class Meta:
        verbose_name = _("Type of other sphere act. employer")
        verbose_name_plural = _("Types of other sphere act. employers")

    def __str__(self):
        return "%s :: %s" % (self.employer_type.name, self.name)


class AbstractWTime(models.Model):
    work_on = models.TimeField(verbose_name=_('Work time from'), blank=True, null=True)
    work_off = models.TimeField(verbose_name=_('Work time to'), blank=True, null=True)
    phone_on = models.TimeField(verbose_name=_('Phone time from'), blank=True, null=True)
    phone_off = models.TimeField(verbose_name=_('Phone time to'), blank=True, null=True)
    employer_profile = models.ManyToManyField(TypeEmployerProfile, verbose_name=_('Types of employer profile'),
                                              blank=True, null=True)
    employer_other = models.ManyToManyField(TypeEmployerOther, verbose_name=_('Types of employer'), blank=True,
                                            null=True)

    class Meta:
        abstract = True

    @property
    def emptypes(self):
        return self.employer_profile.order_by('name').values_list('employer_type__pk', flat=True).distinct()

    def profile_lst(self):
        return self.employer_profile.order_by('-order_in_list', 'name').values_list('pk', flat=True)

    def other_radio(self):
        return self.employer_other.filter(is_radio=True).values_list('employer_type__pk', flat=True).distinct()

    def other_radio_all(self):
        return self.employer_other.filter(is_radio=True)

    def other_multi_all(self):
        return self.employer_other.filter(is_radio=False)

    def other_multi(self):
        return self.employer_other.filter(is_radio=False).values_list('employer_type__pk', flat=True).distinct()

    @property
    def empother(self):
        return self.employer_other.order_by('name').values_list('employer_type__pk', flat=True).distinct()

    @property
    def radio_profiles(self):
        return self.employer_profile.filter(is_radio=True)


class AbstractEmployer(AbstractImg, AbstractWTime):
    is_company = models.BooleanField(verbose_name=_('Employer is company'), default=False)
    name = std_text_field(_('Company name'))
    position = std_text_field(_('Work position'))
    description = models.TextField(verbose_name=_('Activities description '), blank=True, default='')

    class Meta:
        verbose_name = _("Employer")
        verbose_name_plural = _("Employers")
        abstract = True


class Agency(AbstractName):
    class Meta:
        verbose_name = _("Agency")
        verbose_name_plural = _("Agencies")


class AbstractEmployee(AbstractImg):
    agent_name = std_text_field(_('Agent name'))
    agent_phone = models.CharField(max_length=20, verbose_name=_('Mobile phone of agent'), blank=True, default='')
    agent_email = models.EmailField(verbose_name=_('Agent Email'), blank=True, null=True)
    agent_only = models.BooleanField(_('Contact only with agent'), default=False)
    agent_on = models.TimeField(verbose_name=_('Agent work time from'), blank=True, null=True)
    agent_off = models.TimeField(verbose_name=_('Agent work time to'), blank=True, null=True)
    permanent_work = std_text_field(_('Permanent place of work'))
    awards = std_text_field(_('Awards, achievements, titles'))
    payment_from = models.IntegerField(verbose_name=_('Amount payment from'), null=True, blank=True)
    payment_to = models.IntegerField(verbose_name=_('Amount payment to'), null=True, blank=True)
    additionally = models.TextField(verbose_name=_("Additionally"), blank=True, default='')
    source_about_resource = std_text_field(_('Source about our resource'))
    education = models.ManyToManyField(Education, verbose_name=_('Education'), blank=True, null=True)
    agency = models.ManyToManyField(Agency, verbose_name=_('In agency base'), blank=True, null=True)

    class Meta:
        verbose_name = _("Employee")
        verbose_name_plural = _("Employees")
        abstract = True


class CompanyCategory(Tree):
    slug_detail = 'companies_category'

    class Meta:
        ordering = ['parent__id', ]
        verbose_name = _('Company Category')
        verbose_name_plural = _('Companies Categories')

    @property
    def _active_set(self):
        return Company.objects.filter(category=self)


class Company(AbstractName, AbstractLocation, MetaGeo, AbstractWTime, AbstractDate, AbstractTeaser):
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_('Company Admins'),
                                    null=True, blank=True, related_name='%(class)s_comp_adm')
    main_category = models.ForeignKey(CompanyCategory, blank=True, null=True, verbose_name=_('Company category'),
                                      related_name='company', on_delete=models.SET_NULL)
    category = models.ManyToManyField(CompanyCategory, verbose_name=_('All company category'),
                                      related_name='companies')
    fullname = models.CharField(verbose_name=_("Full Name"), max_length=255, db_index=True, blank=True, null=True)
    fullname_en = models.CharField(verbose_name=_('Full Name(English)'), max_length=255, blank=True, null=True,
                                   db_index=True)
    branch = models.BooleanField(verbose_name=_('Is branch?'), default=False, db_index=True)
    parent = models.ForeignKey('self', verbose_name=_('Parent company'), blank=True, null=True, related_name='children',
                               on_delete=models.SET_NULL)

    objects = CompanyManager()

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")

    @property
    def get_fullname(self):
        if get_language() == 'en':
            if self.fullname_en:
                return self.fullname_en
        if self.fullname:
            return self.fullname
        return self.get_name

    @permalink
    def get_absolute_url(self):
        return 'company_detail', (self.pk, ), {}


class CompanyDetail(models.Model):
    company = models.OneToOneField(Company, verbose_name=_('Company'))
    inn = models.CharField(max_length=12, verbose_name=_('INN'), blank=True)
    kpp = models.CharField(max_length=9, verbose_name=_('KPP'), blank=True)
    kpp_add = models.CharField(max_length=9, verbose_name=_('KPP (addon)'), blank=True)
    okato = models.CharField(max_length=11, verbose_name=_('OKATO'), blank=True)
    okpo = models.CharField(max_length=10, verbose_name=_('OKPO'), blank=True)
    ogrn = models.CharField(max_length=13, verbose_name=_('OGRN'), blank=True)
    num_cert_state_reg = models.CharField(max_length=20, verbose_name=_('Number certificate of state registration'),
                                          blank=True)
    date_state_reg = models.DateField(verbose_name=_("Date of state registration"), blank=True, null=True)
    authority_state_reg = models.CharField(max_length=255, verbose_name=_('Authority of state registration'),
                                           blank=True)
    date_ogrn = models.DateField(verbose_name=_("Date of ogrn"), blank=True, null=True)
    authority_ogrn = models.CharField(max_length=255, verbose_name=_('Authority of ogrn'),
                                      blank=True)

    class Meta:
        verbose_name = _("Company detail")
        verbose_name_plural = _("Companies details")


class CompanyWorkTime(AbstractWorkTime):
    company = models.OneToOneField(Company, verbose_name=_('Company'))


@receiver(post_save, sender=Company, dispatch_uid='nnmware_uid')
def create_company_detail(sender, instance, created, **kwargs):
    if created:
        CompanyDetail.objects.create(company=instance)
        CompanyWorkTime.objects.create(company=instance)


class VacancyCategory(Tree):
    slug_detail = 'vacancy_category'

    class Meta:
        ordering = ['parent__id', ]
        verbose_name = _('Vacancy Category')
        verbose_name_plural = _('Vacancy Categories')

    @property
    def _active_set(self):
        return Vacancy.objects.filter(category=self)

VACANCY_UNKNOWN = 0
VACANCY_PERMANENT = 1
VACANCY_CONTRACT = 2
VACANCY_INTERNSHIP = 3
VACANCY_FREELANCE = 4

VACANCY_TYPE = (
    (VACANCY_UNKNOWN, _('Unknown')),
    (VACANCY_PERMANENT, _('Permanent')),
    (VACANCY_CONTRACT, _('Contract')),
    (VACANCY_INTERNSHIP, _('Internship')),
    (VACANCY_FREELANCE, _('Freelance')),
)


class Vacancy(AbstractName, AbstractDate, AbstractTeaser):
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_('Company Admins'),
                                    null=True, blank=True, related_name='%(app_label)s_%(class)s_vac_adm')
    category = models.ForeignKey(VacancyCategory, blank=True, null=True, verbose_name=_('Vacancy category'),
                                 related_name='vacancy', on_delete=models.SET_NULL)
    vacancy_type = models.IntegerField(_("Type of vacancy"), choices=VACANCY_TYPE, default=VACANCY_UNKNOWN,
                                       db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Vacancy owner user'), blank=True,
                             null=True, on_delete=models.SET_NULL)
    company = models.ForeignKey(Company, verbose_name=_('Vacancy owner company'), blank=True, null=True,
                                on_delete=models.SET_NULL)

    objects = VacancyManager()

    class Meta:
        ordering = ['-created_date', ]
        verbose_name = _('Vacancy')
        verbose_name_plural = _('Vacancies')

    @permalink
    def get_absolute_url(self):
        return 'vacancy_detail', (self.pk, ), {}


class AbstractSeller(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), blank=True, null=True)
    company = models.ForeignKey(Company, verbose_name=_('Company'), blank=True, null=True)
    contact_email = models.CharField(verbose_name=_("Contact Email"), blank=True, max_length=75)
    contact_name = models.CharField(max_length=100, verbose_name=_('Contact Name'), blank=True)
    contact_phone = models.CharField(max_length=100, verbose_name=_('Contact Phone'), blank=True)
    expiration_date = models.DateTimeField(_("Date of expiration"), null=True, blank=True)
    sold = models.BooleanField(verbose_name=_('Sold'), default=False)
    corporate = models.BooleanField(verbose_name=_('Is corporate?'), default=False)

    class Meta:
        abstract = True
