#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os

from django import forms
import django
from django.contrib.auth import get_user_model
from django.db.models import FieldDoesNotExist
import utils

HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class UserModelChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        if not kwargs.get('queryset'):
            kwargs['queryset'] = get_user_model().objects.only("name").filter(is_active=True).order_by('name')
        super(UserModelChoiceField, self).__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        return obj.get_full_name()


class UserMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name()


class DisplayCreatorOwnerMixin(object):
    @staticmethod
    def get_owner_display(model, user):
        return user.get_full_name()

    @staticmethod
    def get_creator_display(model, user):
        return user.get_full_name()


class ModelDetail(DisplayCreatorOwnerMixin, object):
    """
    For related fields, __unicode__ method would be the default choice to display in django templates. If a sub-class
    has special display logic, it could implement a static method(@staticmethod) named "get_{field name}_display" to
    customize the output.
    """

    def __init__(self, pk, user, model=None):
        if not model:
            opts = self.Meta
            if opts.model is None:
                raise ValueError('ModelDetail has no model class specified.')
            model = opts.model
        self._meta = {'model': model}
        self._initial_meta()
        self.pk = pk
        self.instance = self._fetch_model()
        self.user = user

    def _initial_meta(self):
        for attr in ['includes', 'excludes', 'related_fields', 'prefetch_fields']:
            self._meta[attr] = getattr(self.Meta, attr, None)

    def detail(self):
        ret = []
        if not self.instance:
            return ret
        for f in self._fields_for_model():
            ret.append(self._detail_field(f))
        return ret

    def _fetch_model(self):
        objects_manager = self._meta['model'].objects
        if self._meta['related_fields']:
            queryset = objects_manager.select_related(*self._meta['related_fields'])
        else:
            queryset = objects_manager.select_related()
        if self._meta['prefetch_fields']:
            queryset = queryset.prefetch_related(*self._meta['prefetch_fields'])
        return queryset.get(pk=self.pk)

    def _detail_field(self, field):
        fname = field.name
        val = getattr(self.instance, fname)
        func_name = 'get_%s_display' % fname
        func = getattr(self, func_name) if hasattr(self, func_name) else None
        if func:
            val = func(self.instance, val)
        elif isinstance(field, django.db.models.fields.IntegerField):
            if field.choices:
                display_method = getattr(self.instance, 'get_%s_display' % fname, None)
                display_val = display_method() if display_method else None
                val = display_val or val

        elif isinstance(field, django.db.models.fields.DateField):
            val = utils.local_time_to_text(val) if val else None

        return {'label': field.verbose_name or fname,
                'name': fname,
                'value': val or ''}

    def _fields_for_model(self):
        meta_fields = self._meta['model']._meta._name_map
        if self._meta['excludes']:
            return (v[0] for k, v in meta_fields.items() if v[2] and k not in self._meta['excludes'])
        elif self._meta['includes']:
            return (v[0] for k, v in meta_fields.items() if v[2] and k in self._meta['includes'])
        else:
            return (v[0] for k, v in meta_fields.items() if v[2])

    class Meta:
        excludes = ('is_active',)
