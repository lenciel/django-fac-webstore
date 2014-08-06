#!/usr/bin/env python
# -*- coding: utf-8 -*-


from django import forms
from django.forms.widgets import CheckboxInput, ClearableFileInput, FileInput
from django.forms.util import flatatt
from django.utils.html import format_html, conditional_escape
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe


class AceCheckboxInput(CheckboxInput):
    """
    Ace风格的Checkbox。
    Ace要求在checkbox后添加一个<span class="lbl"></span>，否则checkbox不会显示。
    """
    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, type='checkbox', name=name)
        if self.check_test(value):
            final_attrs['checked'] = 'checked'
        if not (value is True or value is False or value is None or value == ''):
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_text(value)
        return format_html('<input{0} /><span class="lbl"></span>', flatatt(final_attrs))


class AceClearableFileInput(ClearableFileInput):

    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }
        template = '%(input)s'
        substitutions['input'] = super(FileInput, self).render(name, value, attrs)

        if value and hasattr(value, "url"):
            template = self.template_with_initial
            substitutions['initial'] = format_html('<a href="{0}">{1}</a>',
                                                   value.url,
                                                   force_text(value))
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                #NOTE: only adapt below single line
                #copy from django system lib and replace BooleanField with AceCheckboxInput
                substitutions['clear'] = AceCheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions

        return mark_safe(template % substitutions)


class AceBooleanField(forms.BooleanField):
    """
    Ace风格的BooleanField。

    如果要在Ace的表单中使用BooleanField，必须使用这个AceBooleanField，
    否则这个字段将不能正常显示出来。

    用法：
    from django import forms
    from ace.forms.fields import AceBooleanField

    class MyForm(forms.ModelForm):
        is_group_owner = AceBooleanField(label=u'是否部门领导',
                                        initial=False)

    """
    widget = AceCheckboxInput


class AceImageField(forms.ImageField):
    """
    Ace风格的ClearableFileInput

    如果要在Ace的表单中使用BooleanField，必须使用这个AceImageField，
    否则这个字段将不能正常显示出来。

    """
    widget = AceClearableFileInput

