# -*- coding: utf-8 -*-
from decimal import Decimal
import json
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch
from django import forms
from django.forms import TextInput, Textarea, FileInput, HiddenInput

from nnmware.core.imgutil import make_admin_thumbnail
from nnmware.core.captcha import displayhtml

class ReCaptchaWidget(forms.widgets.Widget):
    recaptcha_challenge_name = 'recaptcha_challenge_field'
    recaptcha_response_name = 'recaptcha_response_field'

    def render(self, name, value, attrs=None):
        return mark_safe(u'%s' % displayhtml(settings.RECAPTCHA_PUBLIC_KEY))

    def value_from_datadict(self, data, files, name):
        return [data.get(self.recaptcha_challenge_name, None), data.get(self.recaptcha_response_name, None)]



class CommentSmileWidget(Textarea):
    class Media:
        js = ('js/smile.js',)


class AdminImageWithThumbnailWidget(FileInput):
    """
    A FileField Widget that shows its current image as a thumbnail if it has one.
    """

    def __init__(self, attrs=None):
        if not attrs:
            attrs = {}
        super(AdminImageWithThumbnailWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = []
        if value and hasattr(value, "url"):
            thumb = make_admin_thumbnail(value.url)
            if not thumb:
                thumb = value.url
            output.append('<a href="%s"><img src="%s" /><br/>%s</a><br/> %s' %\
                          (value.url, thumb, value.url, _('Change:')))
        output.append(super(AdminImageWithThumbnailWidget, self).render(name, value, attrs))
        output.append('<input type="checkbox" name="%s_delete"/> %s' % (name, _(u'Delete')))

        return mark_safe(u''.join(output))

    def value_from_datadict(self, data, files, name):
        if not data.get('%s_delete' % name):
            return super(AdminImageWithThumbnailWidget, self).value_from_datadict(data, files, name)
        else:
            return '__deleted__'


class ImageWithThumbnailWidget(FileInput):
    """
    A FileField Widget that shows its current image as a thumbnail if it has one.
    """

    def __init__(self, attrs=None):
        if not attrs:
            attrs = {}
        super(ImageWithThumbnailWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = []
        if value and hasattr(value, "url"):
            thumb = make_admin_thumbnail(value.url)
            if not thumb:
                thumb = value.url
            output.append('<img src="%s" /><br/><input type="checkbox" name="%s_delete"/>%s<br/> %s' %\
                          (thumb, name, _('Delete'), _('Change:')))
        output.append(super(ImageWithThumbnailWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))

    def value_from_datadict(self, data, files, name):
        if not data.get('%s_delete' % name):
            return super(ImageWithThumbnailWidget, self).value_from_datadict(data, files, name)
        else:
            return '__deleted__'


class AutocompleteWidget(TextInput):
    """
    Autocomplete widget to use with jquery-autocomplete plugin.

    Widget can use for static and dynamic (AJAX-liked) data. Also
    you can relate some fields and it's values'll posted to autocomplete
    view.

    Widget support all jquery-autocomplete options that dumped to JavaScript
    via json.

    **Note** You must init one of ``choices`` or ``choices_url`` attribute.
    Else widget raises TypeError when rendering.
    """

    def __init__(self, attrs=None, choices=None, choices_url=None, options=None, related_fields=None):
        """
        Optional arguments:
        -------------------

            * ``choices`` - Static autocomplete choices (similar to choices
            used in Select widget).

            * ``choices_url`` - Path to autocomplete view or autocomplete
            url name.

            * ``options`` - jQuery autocomplete plugin options. Auto dumped
            to JavaScript via json

            * ``related_fields`` - Fields that relates to current (value
            of this field will sended to autocomplete view via POST)
        """
        self.attrs = attrs or {}
        self.choice, self.choices, self.choices_url = None, choices, choices_url
        self.options = options or {}

        if related_fields:
            extra = {}
            if isinstance(related_fields, str):
                related_fields = list(related_fields)

            for field in related_fields:
                extra[field] = "%s_value" % field

            self.extra = extra
        else:
            self.extra = {}

    def render(self, name, value=None, attrs=None):
        if not self.choices and not self.choices_url:
            raise TypeError('One of "choices" or "choices_url" keyword argument must be supplied obligatory.')

        if self.choices and self.choices_url:
            raise TypeError('Only one of "choices" or "choices_url" keyword argument can be supplied.')

        choices = ''

        if self.choices:
            self.set_current_choice(value)
            choices = json.dumps([unicode(v) for k, v in self.choices], ensure_ascii=False)
            html_code = HiddenInput().render(name, value=value)
            name += '_autocomplete'
        else:
            html_code = ''

        if self.choices_url:
            try:
                choices = json.dumps(reverse(str(self.choices_url)))
            except NoReverseMatch:
                choices = json.dumps(self.choices_url)

        if self.options or self.extra:
            if 'extraParams' in self.options:
                self.options['extraParams'].update(self.extra)
            else:
                self.options['extraParams'] = self.extra

            options = ', ' + json.dumps(self.options, indent=4, sort_keys=True)
            extra = []

            for k, v in self.extra.items():
                options = options.replace(json.dumps(v), v)
                extra.append(u"function %s() { return $('#id_%s').val(); }\n" % (v, k))

            extra = u''.join(extra)
        else:
            extra, options = '', ''

        final_attrs = self.build_attrs(attrs)
        html_code += super(AutocompleteWidget, self).render(name, self.choice or value, attrs)

        html_code += u"""
<script type="text/javascript">
    $(document).ready(function(){
    %s$('#%s')
        // don't navigate away from the field on tab when selecting an item
            .bind( "keydown", function( event ) {
                if ( event.keyCode === $.ui.keyCode.TAB &&
                    $( this ).data( "autocomplete" ).menu.active ) {
                    event.preventDefault();
                }
            })
            .autocomplete({
                source: function( request, response ) {
                $.ajax({
                    url: %s%s,
                    data: { q: extractLast( request.term )},
                    success: function( data ) {
                        response( data.q );
                    }
                });
                },
                select: function( event, ui ) {
                //create formatted friend
                var friend = ui.item.value,
                span = $("<span>").text(friend),
                a = $("<a>").addClass("remove").attr({
                    href: "javascript:",
                    title: "Remove " + friend
                    }).text("x").appendTo(span);
                    //add friend to friend div
                    span.insertBefore("#%s");
                    },
                    change: function() {
                    //prevent 'to' field being updated and correct position
                $("#%s").css("top", 2);
            }

            });
                //add click handler to friends div
                $("#friends").click(function(){
            //focus 'to' field
            $("#%s").focus();
            });
        //add live handler for clicks on remove links
        $(".remove", document.getElementById("friends")).live("click", function(){
            //remove current friend
        $(this).parent().remove();
        //correct 'to' field position
        if($("#friends span").length === 0) {
            $("#%s").css("top", 0);
            }
        });
        });
    </script>
""" % (extra, final_attrs['id'], choices, options, final_attrs['id'], final_attrs['id'], final_attrs['id'], final_attrs['id'])

        return mark_safe(html_code)

    def set_current_choice(self, data):
        if not self.choices:
            raise ValueError('"choices" attribute was not defined yet.')

        for k, v in self.choices:
            if k == data:
                self.choice = v
                break

    def value_from_datadict(self, data, files, name):
        if not self.choices:
            return super(AutocompleteWidget, self).value_from_datadict(data, files, name)

        autocomplete_name = name + '_autocomplete'

        if not autocomplete_name in data:
            self.set_current_choice(data[name])
            return data[name]

        for k, v in self.choices:
            if v == data[autocomplete_name]:
                self.set_current_choice(k)
                return k


class CLEditorWidget(Textarea):
    def __init__(self, *args, **kwargs):
        super(CLEditorWidget, self).__init__(*args, **kwargs)
        self.attrs["class"] = "cleditor"

    class Media:
        css = {"all": ("css/jquery.cleditor.css",)}
        js = ("js/jquery.cleditor.min.js",
              "js/jquery.cleditor.icon.min.js")



