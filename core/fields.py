import os
import json
from django import forms
from django.conf import settings
from django.db import models
from django.db.models import signals
from django.db.models.fields import TextField
from django.db.models.fields.files import ImageField
from django.core.exceptions import ValidationError
from django.db.models.fields.subclassing import SubfieldBase
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from nnmware.core.imgutil import rename_by_field
from nnmware.core.widgets import ImageWithThumbnailWidget, CLEditorWidget
from nnmware.core.widgets import ReCaptchaWidget
from nnmware.core.captcha import submit

class ReCaptchaField(forms.CharField):

    default_error_messages = { 'captcha_invalid': _(u'Invalid captcha')}

    def __init__(self, *args, **kwargs):
        self.widget = ReCaptchaWidget
        self.required = True
        super(ReCaptchaField, self).__init__(*args, **kwargs)

    def clean(self, values):
        super(ReCaptchaField, self).clean(values[1])
        recaptcha_challenge_value = smart_unicode(values[0])
        recaptcha_response_value = smart_unicode(values[1])
        check_captcha = submit(recaptcha_challenge_value, recaptcha_response_value, settings.RECAPTCHA_PRIVATE_KEY, {})
        if not check_captcha.is_valid:
            raise forms.util.ValidationError(self.error_messages['captcha_invalid'])
        return values[0]

class RichTextField(TextField):
    """
    TextField that stores HTML.
    """

    def formfield(self, **kwargs):
        kwargs["widget"] = CLEditorWidget
        formfield = super(RichTextField, self).formfield(**kwargs)
        return formfield

# South requires custom fields to be given "rules".
# See http://south.aeracode.org/docs/customfields.html
if "south" in settings.INSTALLED_APPS:
    try:
        from south.modelsinspector import add_introspection_rules

        add_introspection_rules(rules=[((RichTextField,), [], {})], patterns=["nnmware\.core\.fields\."])
    except ImportError:
        pass


class StdImageFormField(ImageField):
    def clean(self, data, initial=None):
        if data != '__deleted__':
            return super(StdImageFormField, self).clean(data, initial)
        else:
            return '__deleted__'


class ImageWithThumbnailField(ImageField):
    """ ImageField with thumbnail support

        auto_rename: if it is set perform auto rename to
        <class name>-<field name>-<object pk>.<ext>
        on pre_save.
    """

    def __init__(self, verbose_name=None, name=None,
                 width_field=None, height_field=None,
                 auto_rename=None, name_field=None,
                 upload_to=None, **kwargs):
        self.auto_rename = auto_rename

        self.width_field, self.height_field = width_field, height_field
        super(ImageWithThumbnailField, self).__init__(verbose_name, name,
            width_field, height_field,
            upload_to=upload_to,
            **kwargs)
        self.name_field = name_field
        self.auto_rename = auto_rename

    def formfield(self, **kwargs):
        defaults = {'widget': ImageWithThumbnailWidget,
                    'form_class': StdImageFormField}
        defaults.update(kwargs)
        return super(ImageWithThumbnailField, self).formfield(**defaults)

    def save_form_data(self, instance, data):
        """
            Overwrite save_form_data to delete images if "delete" checkbox
            is selected
        """
        if data == '__deleted__':
            filename = getattr(instance, self.name).path
            if os.path.exists(filename):
                _remove_thumbnails(filename)
                os.remove(filename)
            setattr(instance, self.name, None)
        else:
            super(ImageWithThumbnailField, self).save_form_data(instance, data)

    def _save_rename(self, instance, **kwargs):
        if hasattr(self, '_renaming') and self._renaming:
            return
        if self.auto_rename == NOTSET:
            try:
                self.auto_rename = settings.RENAME_IMAGES
            except:
                self.auto_rename = False

        image = getattr(instance, self.name)
        #raise `image`
        if image and self.auto_rename:
            from uuid import uuid4

            image = rename_by_field(image.path, '%s' % str(uuid4()))
            setattr(instance, self.attname, image)
            self._renaming = True
            instance.save()
            self._renaming = False

    def _delete_thumbnail(self, sender, instance=None, **kwargs):
        image = getattr(instance, self.attname)
        if hasattr(image, 'path'):
            remove_file_thumbnails(image.path)

    def contribute_to_class(self, cls, name):
        super(ImageWithThumbnailField, self).contribute_to_class(cls, name)
        signals.pre_delete.connect(self._delete_thumbnail, sender=cls)
        signals.post_save.connect(self._save_rename, sender=cls)



try:
    # South introspection rules for our custom field.
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([(
        (ImageWithThumbnailField, ),
        [],
            {
            'name_field': ["name_field", {"default": None}],
            'auto_rename': ["auto_rename", {"default": None}],
            },
        )], ['^nnmware\.core\.fields'])
except :
    pass


class JSONField(models.TextField):
    """Simple JSON field that stores python structures as JSON strings
    on database.
    """
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        """
        Convert the input JSON value into python structures, raises
        django.core.exceptions.ValidationError if the data can't be converted.
        """
        if self.blank and not value:
            return None
        if isinstance(value, basestring):
            try:
                return json.loads(value)
            except Exception, e:
                raise ValidationError(str(e))
        else:
            return value

    def validate(self, value, model_instance):
        """Check value is a valid JSON string, raise ValidationError on
        error."""
        if isinstance(value, basestring):
            super(JSONField, self).validate(value, model_instance)
            try:
                json.loads(value)
            except Exception, e:
                raise ValidationError(str(e))

    def get_prep_value(self, value):
        """Convert value to JSON string before save"""
        try:
            return json.dumps(value)
        except Exception, e:
            raise ValidationError(str(e))

    def value_to_string(self, obj):
        """Return value from object converted to string properly"""
        return smart_unicode(self.get_prep_value(self._get_val_from_obj(obj)))

    def value_from_object(self, obj):
        """Return value dumped to string."""
        return self.get_prep_value(self._get_val_from_obj(obj))


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ['^nnmware\.core\.fields\.JSONField'])
except :
    pass

def std_text_field(verbose):
    return models.CharField(max_length=256, verbose_name=verbose, blank=True, default='')
