# -*- coding: utf-8 -*-
# nnmware(c)2012-2016
# Dossier admin

from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from nnmware.apps.dossier.models import TypeAppearanceHuman, TypeNationalHuman, TypeBodyHuman, TypeFeatureAppearance, \
    HairColor, EyeColor, SkinColor, HairLength, HairTexture, TypeNational, TypeProfession, TypeLifestyle, \
    TypeBrightAppearance, TypeHistorical, TypeBodyModification, TypeSurvey, ReadinessScene, CreativeActivity, \
    LanguageSkill, LanguageSpeak, SpokenDialect, TypeDance, TypeVocal, TypeMusicInstrument, TypeDrive, TypeSport, \
    TypeSpecialSkill, TypeOtherSkill, DanceSkill, VocalSkill, MusicSkill, DriveSkill, SportSkill, SpecialSkill, \
    OtherSkill, TransportType, TransportMark, AnimalType, AnimalKind, SurveyObjectType, SurveySuitType, RequisiteType, \
    Vehicle, SurveyObject, SurveySuit, Requisite, Animal, Child, ClothingSize, ShoesSize, HeadSize, ChestSize
from nnmware.core.admin import TypeBaseAdmin, BaseSkillInline


@admin.register(TypeAppearanceHuman)
class TypeAppearanceHumanAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Type of appearance"), {"fields": ['name', ]}),)
    ordering = ('position', 'name')


@admin.register(TypeNationalHuman)
class TypeNationalHumanAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("National type"), {"fields": ['name', ]}),)
    ordering = ('position', 'name')


@admin.register(TypeBodyHuman)
class TypeBodyHumanAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Body Type"), {"fields": ['name', ]}),)
    ordering = ('position', 'name')


@admin.register(TypeFeatureAppearance)
class TypeFeatureAppearanceAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Feature appearance"), {"fields": ['name', ]}),)
    ordering = ('position', 'name')


@admin.register(HairColor)
class HairColorAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Hair color"), {"fields": ['name', ]}),)
    ordering = ('position', 'name')


@admin.register(EyeColor)
class EyeColorAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Eye color"), {"fields": ['name', ]}),)
    ordering = ('position', 'name')


@admin.register(SkinColor)
class SkinColorAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Skin color"), {"fields": ['name', ]}),)
    ordering = ('position', 'name')


@admin.register(HairLength)
class HairLengthAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Hair length"), {"fields": ['name', ]}),)
    ordering = ('position', 'name')


@admin.register(HairTexture)
class HairTextureAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Hair texture"), {"fields": ['name', ]}),)
    ordering = ('position', 'name')


@admin.register(TypeNational)
class TypeNationalAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Type on national sign"), {"fields": ['name', ]}),)
    ordering = ('position', 'name')


@admin.register(TypeProfession)
class TypeProfessionAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Type on profession"), {"fields": ['name', ]}),)
    ordering = ('position', 'name')


@admin.register(TypeLifestyle)
class TypeLifestyleAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Type on lifestyle"), {"fields": ['name', ]}),)
    ordering = ('position', 'name')


@admin.register(TypeBrightAppearance)
class TypeBrightAppearanceAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Type on bright appearance"), {"fields": [('name', 'position'), ]}),)
    ordering = ('position', 'name')


@admin.register(TypeHistorical)
class TypeHistoricalAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Type in historical projects"), {"fields": [('name', 'position'), ]}),)
    ordering = ('position', 'name')


@admin.register(TypeBodyModification)
class TypeBodyModificationAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Type body modification"), {"fields": [('name', 'position'), ]}),)
    ordering = ('position', 'name')


@admin.register(TypeSurvey)
class TypeSurveyAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Type of survey"), {"fields": [('name', 'position'), ]}),)
    ordering = ('position', 'name')


@admin.register(ReadinessScene)
class ReadinessSceneAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Readiness in scene"), {"fields": [('name', 'position'), ]}),)
    ordering = ('position', 'name')


@admin.register(CreativeActivity)
class CreativeActivityAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("CreativeActivity"), {"fields": [('name', 'position'), ]}),)
    ordering = ('position', 'name')


class LanguageSkillInline(BaseSkillInline):
    model = LanguageSkill
    fields = (('speak', 'level'),)


@admin.register(LanguageSpeak)
class LanguageSpeakAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Language speak"), {"fields": ['name', ]}),)
    ordering = ('position', 'name')


@admin.register(SpokenDialect)
class SpokenDialectAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Spoken dialect"), {"fields": ['name', ]}),)
    ordering = ('position', 'name')


@admin.register(TypeDance)
class TypeDanceAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Type of dance"), {"fields": ['name', ]}),)
    ordering = ('position', 'name')


@admin.register(TypeVocal)
class TypeVocalAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Type of vocal"), {"fields": ['name', ]}),)
    ordering = ('position', 'name')


@admin.register(TypeMusicInstrument)
class TypeMusicInstrumentAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Type of music instrument"), {"fields": ['name', ]}),)
    ordering = ('position', 'name')


@admin.register(TypeDrive)
class TypeDriveAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Type of driving"), {"fields": ['name', ]}),)
    ordering = ('position', 'name')


@admin.register(TypeSport)
class TypeSportAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Type of sport"), {"fields": ['name', ]}),)
    ordering = ('position', 'name')


@admin.register(TypeSpecialSkill)
class TypeSpecialSkillAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Type of special skill"), {"fields": ['name', ]}),)
    ordering = ('position', 'name')


@admin.register(TypeOtherSkill)
class TypeOtherSkillAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Type of other skill"), {"fields": ['name', ]}),)
    ordering = ('position', 'name')


class DanceSkillInline(BaseSkillInline):
    model = DanceSkill


class VocalSkillInline(BaseSkillInline):
    model = VocalSkill


class MusicSkillInline(BaseSkillInline):
    model = MusicSkill


class DriveSkillInline(BaseSkillInline):
    model = DriveSkill


class SportSkillInline(BaseSkillInline):
    model = SportSkill


class SpecialSkillInline(BaseSkillInline):
    model = SpecialSkill


class OtherSkillInline(BaseSkillInline):
    model = OtherSkill


@admin.register(TransportType)
class TTypeAdmin(TypeBaseAdmin):
    fieldsets = ((_("Type of vehicle"), {"fields": ['name', ]}),)


@admin.register(TransportMark)
class TMarkAdmin(TypeBaseAdmin):
    fieldsets = ((_("Mark of vehicle"), {"fields": ['name', ]}),)


@admin.register(AnimalType)
class AnimalTypeAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Type of animal"), {"fields": ['name', ]}),)
    ordering = ('position', 'name')


@admin.register(AnimalKind)
class AnimalKindAdmin(TypeBaseAdmin):
    fieldsets = ((_("Kind of animal"), {"fields": ['name', ]}),)
    ordering = ('name', )


@admin.register(SurveyObjectType)
class SurveyObjectTypeAdmin(TypeBaseAdmin):
    list_display = ('name', 'position')
    fieldsets = ((_("Type of survey object"), {"fields": ['name', ]}),)
    ordering = ('position', 'name')


@admin.register(SurveySuitType)
class SurveySuitTypeAdmin(TypeBaseAdmin):
    list_display = ('name', 'overall')
    fieldsets = ((_("Type of survey suit"), {"fields": ['name', 'overall']}),)
    ordering = ('position', 'name')


@admin.register(RequisiteType)
class RequisiteTypeAdmin(TypeBaseAdmin):
    fieldsets = ((_("Type of requisite"), {"fields": ['name', ]}),)
    ordering = ('position', 'name')


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('ttype', 'tmark', 'name')
    search_fields = ('description',)
    fieldsets = (
        (_("Vehicle"), {"fields": [('ttype', 'tmark'),
                                   ('description',), ]}),
    )
    ordering = ('ttype', 'name')


@admin.register(SurveyObject)
class SurveyObjectAdmin(admin.ModelAdmin):
    list_display = ('stype', 'name')
    search_fields = ('description',)
    fieldsets = (
        (_("Survey object"), {"fields": [('stype', 'name'),
                                   ('description',), ]}),
    )
    ordering = ('stype', 'name')


@admin.register(SurveySuit)
class SurveySuitAdmin(admin.ModelAdmin):
    list_display = ('stype', 'name')
    search_fields = ('description',)
    fieldsets = (
        (_("Survey suit"), {"fields": [('stype', 'name'), ('description',)]}),
    )
    ordering = ('stype', 'name')


@admin.register(Requisite)
class RequisiteAdmin(admin.ModelAdmin):
    list_display = ('rtype', 'name')
    search_fields = ('description',)
    fieldsets = (
        (_("Requisite"), {"fields": [('rtype', 'name'), ('description',)]}),
    )
    ordering = ('rtype', 'name')


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('animal', 'animalkind', 'name')
    search_fields = ('description',)
    fieldsets = (
        (_("Animal"), {"fields": [('animal', 'name'), ('animalkind',), ('description',), ]}),
    )
    ordering = ('animal', 'name')


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'birthdate', 'twins')
    search_fields = ('name',)
    fieldsets = (
        (_("Child"), {"fields": [('name', 'gender'), ('birthdate', 'twins'), ('description',), ]}),
    )
    ordering = ('name', 'gender')


@admin.register(ClothingSize)
class ClothingSizeAdmin(admin.ModelAdmin):
    list_display = ('international', 'russian', 'dest')
    search_fields = ('international',)
    fieldsets = (
        (_("Clothing size"), {"fields": [('international', 'russian'), ('eu', 'uk', 'us'), ('dest', )]}),
    )
    ordering = ('international', )


@admin.register(ShoesSize)
class ShoesSizeAdmin(admin.ModelAdmin):
    list_display = ('cm', 'ru', 'eu', 'us', 'dest')
    search_fields = ('cm',)
    fieldsets = (
        (_("Shoes size"), {"fields": [('cm', 'ru'), ('eu', 'us'), ('dest', )]}),
    )
    ordering = ('cm', )


@admin.register(HeadSize)
class HeadSizeAdmin(admin.ModelAdmin):
    list_display = ('international', 'russian', 'dest')
    search_fields = ('international',)
    fieldsets = (
        (_("Head size"), {"fields": [('international', 'russian', 'dest')]}),
    )
    ordering = ('russian', )


@admin.register(ChestSize)
class ChestSizeAdmin(admin.ModelAdmin):
    list_display = ('international', 'russian')
    search_fields = ('international',)
    fieldsets = (
        (_("Chest size"), {"fields": [('international', 'russian')]}),
    )
    ordering = ('russian', )
