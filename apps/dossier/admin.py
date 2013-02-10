
from django.contrib import admin
from nnmware.apps.dossier.models import *
from django.utils.translation import ugettext_lazy as _
from nnmware.core.admin import TypeBaseAdmin, BaseSkillInline

class TypeAppearanceHumanAdmin(TypeBaseAdmin):
    fieldsets = ((_("Type of appearance"), {"fields": [('name'),]}),)

class TypeNationalHumanAdmin(TypeBaseAdmin):
    fieldsets = ((_("National type"), {"fields": [('name'),]}),)

class TypeBodyHumanAdmin(TypeBaseAdmin):
    fieldsets = ((_("Body Type"), {"fields": [('name'),]}),)

class TypeFeatureAppearanceHumanAdmin(TypeBaseAdmin):
    fieldsets = ((_("Feature appearance"), {"fields": [('name'),]}),)

class HairColorAdmin(TypeBaseAdmin):
    fieldsets = ((_("Hair color"), {"fields": [('name'),]}),)

class EyeColorAdmin(TypeBaseAdmin):
    fieldsets = ((_("Eye color"), {"fields": [('name'),]}),)

class SkinColorAdmin(TypeBaseAdmin):
    fieldsets = ((_("Skin color"), {"fields": [('name'),]}),)

class HairLengthAdmin(TypeBaseAdmin):
    fieldsets = ((_("Hair length"), {"fields": [('name'),]}),)

class HairTextureAdmin(TypeBaseAdmin):
    fieldsets = ((_("Hair texture"), {"fields": [('name'),]}),)

class TypeNationalAdmin(TypeBaseAdmin):
    fieldsets = ((_("Type on national sign"), {"fields": [('name'),]}),)

class TypeProfessionAdmin(TypeBaseAdmin):
    fieldsets = (
        (_("Type on profession"), {"fields": [('name'),
                                              ]}),)

class TypeLifestyleAdmin(TypeBaseAdmin):
    fieldsets = (
        (_("Type on lifestyle"), {"fields": [('name'),
                                             ]}),)

class TypeBrightAppearanceAdmin(TypeBaseAdmin):
    fieldsets = (
        (_("Type on bright appearance"), {"fields": [('name','order_in_list'),
                                                     ]}),)

class TypeHistoricalAdmin(TypeBaseAdmin):
    fieldsets = (
        (_("Type in historical projects"), {"fields": [('name','order_in_list'),
                                                       ]}),)

class TypeSurveyAdmin(TypeBaseAdmin):
    fieldsets = ((_("Type of survey"), {"fields": [('name','order_in_list'),]}),)


class CreativeActivityAdmin(TypeBaseAdmin):
    fieldsets = (
        (_("CreativeActivity"), {"fields": [('name','order_in_list'),
                                            ]}),)

class LanguageSkillInline(BaseSkillInline):
    model = LanguageSkill
    fields = (('speak','level'),)

class LanguageSpeakAdmin(TypeBaseAdmin):
    fieldsets = (
        (_("Language speak"), {"fields": [('name'),
                                          ]}),)

class TypeDanceAdmin(TypeBaseAdmin):
    fieldsets = (
        (_("Type of dance"), {"fields": [('name'),
                                         ]}),)

class TypeVocalAdmin(TypeBaseAdmin):
    fieldsets = (
        (_("Type of vocal"), {"fields": [('name'),
                                         ]}),)

class TypeMusicInstrumentAdmin(TypeBaseAdmin):
    fieldsets = ((_("Type of music instrument"), {"fields": [('name'),]}),)

class TypeDriveAdmin(TypeBaseAdmin):
    fieldsets = ((_("Type of driving"), {"fields": [('name'),]}),)

class TypeSportAdmin(TypeBaseAdmin):
    fieldsets = ((_("Type of sport"), {"fields": [('name'),]}),)

class TypeSpecialSkillAdmin(TypeBaseAdmin):
    fieldsets = ((_("Type of special skill"), {"fields": [('name'),]}),)

class TypeOtherSkillAdmin(TypeBaseAdmin):
    fieldsets = ((_("Type of other skill"), {"fields": [('name'),]}),)

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
    fieldsets = ((_("Type of vehicle"), {"fields": [('name'),]}),)

class TMarkAdmin(TypeBaseAdmin):
    fieldsets = ((_("Mark of vehicle"), {"fields": [('name'),]}),)

class AnimalTypeAdmin(TypeBaseAdmin):
    fieldsets = ((_("Type of animal"), {"fields": [('name'),]}),)

class AnimalKindAdmin(TypeBaseAdmin):
    fieldsets = ((_("Kind of animal"), {"fields": [('name'),]}),)

class SurveyObjectTypeAdmin(TypeBaseAdmin):
    fieldsets = ((_("Type of survey object"), {"fields": [('name'),]}),)

class SurveySuitTypeAdmin(TypeBaseAdmin):
    fieldsets = ((_("Type of survey suit"), {"fields": [('name'),]}),)

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
