# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from nnmware.apps.address.models import Institution
from django.utils.translation import ugettext_lazy as _
from nnmware.core.abstract import AbstractOrder
from nnmware.core.fields import std_text_field
from nnmware.core.utils import tuplify, current_year

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

class AppearanceType(AbstractOrder):
    name = std_text_field(_('Type of appearance'))

    class Meta:
        verbose_name = _("Type of appearance")
        verbose_name_plural = _("Types of appearance")

class NationalType(AbstractOrder):
    name = std_text_field(_('National Type'))

    class Meta:
        verbose_name = _("National Type")
        verbose_name_plural = _("National Types")


class BodyType(AbstractOrder):
    name = std_text_field(_('Body Type'))

    class Meta:
        verbose_name = _("Body Type")
        verbose_name_plural = _("Body Types")

class FeatureAppearance(AbstractOrder):
    name = std_text_field(_('Feature of appearance'))

    class Meta:
        verbose_name = _("Feature appearance")
        verbose_name_plural = _("Feature appearances")

class HairColor(AbstractOrder):
    name = std_text_field(_('Hair color'))

    class Meta:
        verbose_name = _("Hair color")
        verbose_name_plural = _("Hair colors")

class HairLength(AbstractOrder):
    name = std_text_field(_('Length of hair'))

    class Meta:
        verbose_name = _("Length of hair")
        verbose_name_plural = _("Length of hair")

class HairTexture(AbstractOrder):
    name = std_text_field(_('Texture of hair'))

    class Meta:
        verbose_name = _("Texture of hair")
        verbose_name_plural = _("Textures of hair")

class SkinColor(AbstractOrder):
    name = std_text_field(_('Skin color'))

    class Meta:
        verbose_name = _("Color of skin")
        verbose_name_plural = _("Colors of skin")

class ActorCategory(AbstractOrder):
    name = std_text_field(_('Category of actor'))

    class Meta:
        verbose_name = _("Category of actor")
        verbose_name_plural = _("Categories of actors")

    @property
    def get_random_img(self):
        all_actors = self.actor_set.order_by('?')
        for actor in all_actors:
            if actor.ava <> settings.DEFAULT_AVATAR:
                return actor.ava
        return settings.DEFAULT_AVATAR


class TypeNational(AbstractOrder):
    name = std_text_field(_('Type on national sign'))

    class Meta:
        verbose_name = _("Type on national sign")
        verbose_name_plural = _("Types on national sign")

class TypeProfession(AbstractOrder):
    name = std_text_field(_('Type on profession'))

    class Meta:
        verbose_name = _("Type on profession")
        verbose_name_plural = _("Types on profession")

class TypeLifestyle(AbstractOrder):
    name = std_text_field(_('Type on lifestyle'))

    class Meta:
        verbose_name = _("Type on lifestyle")
        verbose_name_plural = _("Types on lifestyle")

class TypeBrightAppearance(AbstractOrder):
    name = std_text_field(_('Type on bright appearance'))

    class Meta:
        verbose_name = _("Type on bright appearance")
        verbose_name_plural = _("Types on bright appearance")

class TypeHistorical(AbstractOrder):
    name = std_text_field(_('Type in historical projects'))

    class Meta:
        verbose_name = _("Type in historical projects")
        verbose_name_plural = _("Types in historical projects")

class TypeSurvey(AbstractOrder):
    name = std_text_field(_('Type of survey'))

    class Meta:
        verbose_name = _("Type of survey")
        verbose_name_plural = _("Types of surveys")

class CreativeActivity(AbstractOrder):
    name = std_text_field(_('Creative activity'))

    class Meta:
        verbose_name = _("Creative activity")
        verbose_name_plural = _("Creative activities")

class CreativeActivityPerson(AbstractOrder):
    activity = models.ForeignKey(CreativeActivity, verbose_name=_('Creative activity'))
    description = std_text_field(_('Description'))

    class Meta:
        verbose_name = _("Creative activity")
        verbose_name_plural = _("Creative activities")

    def __unicode__(self):
        return "%s" % self.activity.name

