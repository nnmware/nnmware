from django.contrib import admin
from nnmware.apps.dossier.models import *
from django.utils.translation import ugettext_lazy as _
from nnmware.core.admin import TypeBaseAdmin, BaseSkillInline


class TypeAppearanceHumanAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("Type of appearance"), {"fields": ['name', ]}),)
    ordering = ('-order_in_list', 'name')


class TypeNationalHumanAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("National type"), {"fields": ['name', ]}),)
    ordering = ('-order_in_list', 'name')


class TypeBodyHumanAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("Body Type"), {"fields": ['name', ]}),)
    ordering = ('-order_in_list', 'name')


class TypeFeatureAppearanceHumanAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("Feature appearance"), {"fields": ['name', ]}),)
    ordering = ('-order_in_list', 'name')


class HairColorAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("Hair color"), {"fields": ['name', ]}),)
    ordering = ('-order_in_list', 'name')


class EyeColorAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("Eye color"), {"fields": ['name', ]}),)
    ordering = ('-order_in_list', 'name')


class SkinColorAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("Skin color"), {"fields": ['name', ]}),)
    ordering = ('-order_in_list', 'name')


class HairLengthAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("Hair length"), {"fields": ['name', ]}),)
    ordering = ('-order_in_list', 'name')


class HairTextureAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("Hair texture"), {"fields": ['name', ]}),)
    ordering = ('-order_in_list', 'name')


class TypeNationalAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("Type on national sign"), {"fields": ['name', ]}),)
    ordering = ('-order_in_list', 'name')


class TypeProfessionAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("Type on profession"), {"fields": ['name', ]}),)
    ordering = ('-order_in_list', 'name')


class TypeLifestyleAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("Type on lifestyle"), {"fields": ['name', ]}),)
    ordering = ('-order_in_list', 'name')


class TypeBrightAppearanceAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("Type on bright appearance"), {"fields": [('name', 'order_in_list'), ]}),)
    ordering = ('-order_in_list', 'name')


class TypeHistoricalAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("Type in historical projects"), {"fields": [('name', 'order_in_list'), ]}),)
    ordering = ('-order_in_list', 'name')


class TypeSurveyAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("Type of survey"), {"fields": [('name', 'order_in_list'), ]}),)
    ordering = ('-order_in_list', 'name')


class ReadinessSceneAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("Readiness in scene"), {"fields": [('name', 'order_in_list'), ]}),)
    ordering = ('-order_in_list', 'name')


class CreativeActivityAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("CreativeActivity"), {"fields": [('name', 'order_in_list'), ]}),)
    ordering = ('-order_in_list', 'name')


class LanguageSkillInline(BaseSkillInline):
    model = LanguageSkill
    fields = (('speak', 'level'),)


class LanguageSpeakAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("Language speak"), {"fields": ['name', ]}),)
    ordering = ('-order_in_list', 'name')


class TypeDanceAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("Type of dance"), {"fields": ['name', ]}),)
    ordering = ('-order_in_list', 'name')


class TypeVocalAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("Type of vocal"), {"fields": ['name', ]}),)
    ordering = ('-order_in_list', 'name')


class TypeMusicInstrumentAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("Type of music instrument"), {"fields": ['name', ]}),)
    ordering = ('-order_in_list', 'name')


class TypeDriveAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("Type of driving"), {"fields": ['name', ]}),)
    ordering = ('-order_in_list', 'name')


class TypeSportAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("Type of sport"), {"fields": ['name', ]}),)
    ordering = ('-order_in_list', 'name')


class TypeSpecialSkillAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("Type of special skill"), {"fields": ['name', ]}),)
    ordering = ('-order_in_list', 'name')


class TypeOtherSkillAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("Type of other skill"), {"fields": ['name', ]}),)
    ordering = ('-order_in_list', 'name')


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


class TTypeAdmin(TypeBaseAdmin):
    fieldsets = ((_("Type of vehicle"), {"fields": ['name', ]}),)


class TMarkAdmin(TypeBaseAdmin):
    fieldsets = ((_("Mark of vehicle"), {"fields": ['name', ]}),)


class AnimalTypeAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("Type of animal"), {"fields": ['name', ]}),)
    ordering = ('-order_in_list', 'name')


class AnimalKindAdmin(TypeBaseAdmin):
    fieldsets = ((_("Kind of animal"), {"fields": ['name', ]}),)
    ordering = ('name', )


class SurveyObjectTypeAdmin(TypeBaseAdmin):
    list_display = ('name', 'order_in_list')
    fieldsets = ((_("Type of survey object"), {"fields": ['name', ]}),)
    ordering = ('-order_in_list', 'name')


class SurveySuitTypeAdmin(TypeBaseAdmin):
    list_display = ('name', 'overall')
    fieldsets = ((_("Type of survey suit"), {"fields": ['name', 'overall' ]}),)
    ordering = ('-order_in_list', 'name')


class RequisiteTypeAdmin(TypeBaseAdmin):
    fieldsets = ((_("Type of requisite"), {"fields": ['name', ]}),)
    ordering = ('-order_in_list', 'name')


class VehicleAdmin(admin.ModelAdmin):
    list_display = ('ttype', 'tmark', 'name')
    search_fields = ('description',)
    fieldsets = (
        (_("Vehicle"), {"fields": [('ttype', 'tmark'),
                                   ('description',), ]}),
    )
    ordering = ('ttype', 'name')


class SurveyObjectAdmin(admin.ModelAdmin):
    list_display = ('stype', 'name')
    search_fields = ('description',)
    fieldsets = (
        (_("Survey object"), {"fields": [('stype', 'name'),
                                   ('description',), ]}),
    )
    ordering = ('stype', 'name')


class SurveySuitAdmin(admin.ModelAdmin):
    list_display = ('stype', 'name')
    search_fields = ('description',)
    fieldsets = (
        (_("Survey suit"), {"fields": [('stype', 'name'),
                                         ('description',), ]}),
    )
    ordering = ('stype', 'name')


class RequisiteAdmin(admin.ModelAdmin):
    list_display = ('rtype', 'name')
    search_fields = ('description',)
    fieldsets = (
        (_("Requisite"), {"fields": [('rtype', 'name'),
                                       ('description',), ]}),
    )
    ordering = ('rtype', 'name')


class AnimalAdmin(admin.ModelAdmin):
    list_display = ('animal', 'animalkind', 'name')
    search_fields = ('description',)
    fieldsets = (
        (_("Animal"), {"fields": [('animal', 'name'),('animalkind',),
                                         ('description',), ]}),
    )
    ordering = ('animal', 'name')


class ChildAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'birthdate','twins')
    search_fields = ('name',)
    fieldsets = (
        (_("Child"), {"fields": [('name', 'gender'), ('birthdate', 'twins'), ('description',), ]}),
    )
    ordering = ('name', 'gender')


admin.site.register(TypeDance, TypeDanceAdmin)
admin.site.register(TypeVocal, TypeVocalAdmin)
admin.site.register(TypeMusicInstrument, TypeMusicInstrumentAdmin)
admin.site.register(TypeDrive, TypeDriveAdmin)
admin.site.register(TypeSport, TypeSportAdmin)
admin.site.register(TypeSpecialSkill, TypeSpecialSkillAdmin)
admin.site.register(TypeOtherSkill, TypeOtherSkillAdmin)
admin.site.register(LanguageSpeak, LanguageSpeakAdmin)
admin.site.register(TypeNationalHuman, TypeNationalHumanAdmin)
admin.site.register(TypeBodyHuman, TypeBodyHumanAdmin)
admin.site.register(TypeAppearanceHuman, TypeAppearanceHumanAdmin)
admin.site.register(TypeFeatureAppearanceHuman, TypeFeatureAppearanceHumanAdmin)
admin.site.register(HairColor, HairColorAdmin)
admin.site.register(EyeColor, EyeColorAdmin)
admin.site.register(SkinColor, SkinColorAdmin)
admin.site.register(HairLength, HairLengthAdmin)
admin.site.register(HairTexture, HairTextureAdmin)
admin.site.register(TypeNational, TypeNationalAdmin)
admin.site.register(TypeProfession, TypeProfessionAdmin)
admin.site.register(TypeLifestyle, TypeLifestyleAdmin)
admin.site.register(TypeBrightAppearance, TypeBrightAppearanceAdmin)
admin.site.register(TypeHistorical, TypeHistoricalAdmin)
admin.site.register(CreativeActivity, CreativeActivityAdmin)
admin.site.register(TypeSurvey, TypeSurveyAdmin)
admin.site.register(TransportType, TTypeAdmin)
admin.site.register(TransportMark, TMarkAdmin)
admin.site.register(AnimalType, AnimalTypeAdmin)
admin.site.register(AnimalKind, AnimalKindAdmin)
admin.site.register(SurveyObjectType, SurveyObjectTypeAdmin)
admin.site.register(SurveySuitType, SurveySuitTypeAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(SurveyObject, SurveyObjectAdmin)
admin.site.register(SurveySuit, SurveySuitAdmin)
admin.site.register(Animal, AnimalAdmin)
admin.site.register(Child, ChildAdmin)
admin.site.register(RequisiteType, RequisiteTypeAdmin)
admin.site.register(Requisite, RequisiteAdmin)
admin.site.register(ReadinessScene, ReadinessSceneAdmin)

