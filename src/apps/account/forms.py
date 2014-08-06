#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os

from django import forms
from django.contrib import auth
from django.contrib.auth.models import Group, Permission
from django.core.urlresolvers import reverse
from apps.common import exceptions
from apps.common.ace import AceBooleanField
from apps.common.admin.datatables import DatatablesBuilder, DatatablesIdColumn, DatatablesTextColumn, DatatablesDateTimeColumn, DatatablesBooleanColumn, DatatablesActionsColumn, \
    DatatablesColumnActionsRender


logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))

PERM_CODE_NAMES = [
    'change_product',
    'change_customer',
    'view_customer',
    'change_order',
    'view_order',
]


class UserEditForm(forms.ModelForm):
    is_superuser = AceBooleanField(label=u'是否管理员',
                                   initial=False,
                                   required=False)

    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.fields['user_permissions'].widget.attrs['class'] = "col-md-10"
        self.fields['groups'].widget.attrs['class'] = "col-md-10 "
        self.fields['user_permissions'].queryset = Permission.objects.filter(codename__in=PERM_CODE_NAMES)
        if self.instance.pk:
            self.fields['email'].widget.attrs['readonly'] = True
        self.fields['email'].widget.attrs['class'] = "required xlarge-input"
        if "password" in self.fields:
            self.fields['password'].widget = forms.PasswordInput(
                attrs={'class': "required xlarge-input",
                       'placeholder': u'确认密码，必填项'})

    class Meta:
        model = auth.get_user_model()
        fields = ('email', 'name', 'phone', 'gender', 'is_superuser', 'groups', 'user_permissions')


class UserCreateForm(UserEditForm):
    confirm_password = forms.CharField(label=u'确认密码',
                                       widget=forms.PasswordInput(attrs={
                                            'class': "required xlarge-input",
                                            'placeholder': u'确认密码，必填项'}))

    class Meta:
        model = auth.get_user_model()
        fields = ('email', 'name', 'phone', 'gender', 'is_superuser', 'groups',
                  'user_permissions', 'password', 'confirm_password')

    def save(self, commit=False):
        # 保存新用户的密码
        user = super(UserCreateForm, self).save(commit)
        user.set_password(self.cleaned_data['password'])
        user.is_staff = True
        user.save()
        return user


class UserDatatablesBuilder(DatatablesBuilder):

    id = DatatablesIdColumn()

    email = DatatablesTextColumn(label=u'账号',
                                 is_searchable=True)

    name = DatatablesTextColumn(label=u'用户名',
                                is_searchable=True)

    is_active = DatatablesBooleanColumn((('', u'全部'), (1, u'激活'), (0, u'锁定')),
                                        label='状态',
                                        is_searchable=True,
                                        col_width='7%',
                                        render=(lambda request, model, field_name:
                                                u'<span class="label label-info"> 启用 </span>' if model.is_active else
                                                u'<span class="label label-warning"> 禁用 </span>'))

    is_superuser = DatatablesBooleanColumn(label=u'管理员',
                                           col_width='5%',
                                           is_searchable=True)

    date_joined = DatatablesDateTimeColumn(label=u'创建时间')

    def actions_render(request, model, field_name):
        if model.is_active:
            actions = [{'is_link': False, 'name': 'lock', 'text': u'锁定',
                        'icon': 'icon-lock', 'url_name': 'admin:account:user_lock'},
                       {'is_link': False, 'name': 'password_reset', 'text': u'重置密码',
                        'icon': 'icon-edit', 'url': reverse('admin:account:password_reset'), 'action_type': 'POST',
                        'extra': {'email': model.email}}]
        else:
            actions = [{'is_link': False, 'name': 'unlock', 'text': u'解锁',
                        'icon': 'icon-unlock', 'url_name': 'admin:account:user_unlock'}]
        actions.append({'is_link': True, 'name': 'edit', 'text': u'编辑',
                        'icon': 'icon-edit', 'url_name': 'admin:account:user_edit'})
        return DatatablesColumnActionsRender(actions).render(request, model, field_name)

    _actions = DatatablesActionsColumn(render=actions_render)


class GroupForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        self.fields['permissions'].widget.attrs['class'] = "col-md-10"
        self.fields['permissions'].queryset = Permission.objects.filter(codename__in=PERM_CODE_NAMES)

    class Meta:
        model = Group
        fields = ('name', 'permissions')


class GroupDatatablesBuilder(DatatablesBuilder):

    id = DatatablesIdColumn()

    name = DatatablesTextColumn(label=u'名称',
                                is_searchable=True)


class UserChangePasswordForm(forms.ModelForm):
    old_password = forms.CharField(label=u'旧密码', required=True)

    new_password = forms.CharField(label=u'新密码', required=True)

    confirm_password = forms.CharField(label=u'确认密码', required=True)

    def __init__(self, *args, **kwargs):
        super(UserChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget = forms.PasswordInput(
            attrs={'class': "required", 'placeholder': u'旧密码，必填项'})
        self.fields['new_password'].widget = forms.PasswordInput(
            attrs={'class': "required", 'placeholder': u'新密码，必填项'})
        self.fields['confirm_password'].widget = forms.PasswordInput(
            attrs={'class': "required", 'placeholder': u'再次输入密码，必填项'})

    def clean(self):
        if any(self.errors):
            return ""
        cleaned_data = super(UserChangePasswordForm, self).clean()
        request_user = self.initial['request'].user
        result = None
        if cleaned_data['new_password'] != cleaned_data['confirm_password']:
            result = exceptions.build_response_result(exceptions.ERROR_CODE_NEW_PASSWORD_NOT_MATCH)
        else:
            if self.instance.id == request_user.id:
                # 修改自己的密码前需要先认证
                user = auth.authenticate(username=request_user.email,
                                         password=cleaned_data['old_password'])
                if not user:
                    result = exceptions.build_response_result(exceptions.ERROR_CODE_AUTH_FAILED_INVALID_USERNAME_OR_PASSWORD)
            elif request_user.is_superuser:
                pass
            else:
                result = exceptions.build_response_result(exceptions.ERROR_CODE_PERMISSION_DENY)
        if result:
            raise forms.ValidationError(result['errmsg'])
        return cleaned_data

    def save(self, commit=False):
        user = super(UserChangePasswordForm, self).save(commit)
        user.set_password(self.cleaned_data['new_password'])
        user.save()
        return user

    class Meta:
        model = auth.get_user_model()
        fields = ('old_password', 'new_password', 'confirm_password')
