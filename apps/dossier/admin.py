from django.contrib import admin
from nnmware.apps.dossier.models import *
from django.utils.translation import ugettext_lazy as _
from nnmware.core.admin import TypeBaseAdmin

class AppearanceTypeAdmin(TypeBaseAdmin):
    fieldsets = ((_("Type of appearance"), {"fields": [('name'),]}),)

class NationalTypeAdmin(TypeBaseAdmin):
    fieldsets = ((_("National type"), {"fields": [('name'),]}),)

class BodyTypeAdmin(TypeBaseAdmin):
    fieldsets = ((_("Body Type"), {"fields": [('name'),]}),)

class FeatureAppearanceAdmin(TypeBaseAdmin):
    fieldsets = ((_("Feature appearance"), {"fields": [('name'),]}),)

class HairColorAdmin(TypeBaseAdmin):
    fieldsets = ((_("Hair color"), {"fields": [('name'),]}),)

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

class EventAddonAdmin(TypeBaseAdmin):
    fieldsets = (
        (_("Event addon"), {"fields": [('name','order_in_list'),
                                       ]}),)

class EventCategoryAdmin(TypeBaseAdmin):
    fieldsets = (
        (_("Event category"), {"fields": [('name','order_in_list'),
                                          ]}),)





admin.site.register(NationalType, NationalTypeAdmin)
admin.site.register(BodyType, BodyTypeAdmin)
admin.site.register(AppearanceType, AppearanceTypeAdmin)
admin.site.register(FeatureAppearance, FeatureAppearanceAdmin)
admin.site.register(HairColor, HairColorAdmin)
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
