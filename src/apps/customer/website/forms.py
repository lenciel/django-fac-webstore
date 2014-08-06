#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os

from django import forms
from django.contrib import auth

from apps.customer.models import ShipAddress, Customer


HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class ShipAddressForm(forms.ModelForm):

    def __init__(self, customer, *args, **kwargs):
        super(ShipAddressForm, self).__init__(*args, **kwargs)
        self.customer = customer

    def save(self, commit=False):
        ship_address = super(ShipAddressForm, self).save(commit)
        if self.cleaned_data['is_default']:
            # clean old ones
            self.customer.ship_addresses.update(is_default=False)
            ship_address.is_default = True
        ship_address.owner = self.customer
        ship_address.save()
        return ship_address

    class Meta:
        model = ShipAddress
        fields = ('receiver', 'address', 'address_province', 'address_city', 'address_district', 'mobile', 'tel', 'email', 'is_default')


class ProfileBaseForm(forms.ModelForm):
    name = forms.CharField(max_length=30,
                           widget=forms.TextInput(attrs={"required": "true"}))
    phone = forms.RegexField(regex='^1\d{10}$',
                             error_message=u'手机号码不正确',
                             widget=forms.TextInput(attrs={"required": "true"}))
    company_name = forms.CharField(max_length=128,
                                   widget=forms.TextInput(attrs={"required": "true"}))

    def save(self, commit=False):
        customer = super(ProfileBaseForm, self).save(commit)
        province = self.data['company_address_province']
        city = self.data['company_address_city']
        district = self.data['company_address_district']
        street = self.data['company_address_street']
        customer.company_address = '_'.join([province, city, district, street])
        customer.save()
        return customer

    class Meta:
        model = Customer
        fields = ('name', 'phone', 'company_name')


class ProfileChangePasswordForm(forms.ModelForm):
    old_password = forms.CharField(label=u'当前登录密码',
        widget=forms.PasswordInput(attrs={"required": "true"}),
        help_text=u'必填.')

    password1 = forms.CharField(label=u'新密码',
        widget=forms.PasswordInput(attrs={"required": "true"}),
        help_text=u'必填.')

    password2 = forms.CharField(label=u'确认新密码',
        widget=forms.PasswordInput(attrs={"required": "true"}),
        help_text=u'必填. 请再次输入密码以确认.')

    def clean_old_password(self):
        password = self.cleaned_data.get('old_password')
        user = auth.authenticate(email=self.instance.email, password=password)
        if not user:
            raise forms.ValidationError(u'当前登录密码不正确')
        return password

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(u'两次输入的密码不匹配')
        return password2

    def save(self):
        user = self.instance
        new_password = self.cleaned_data['password2']
        user.set_password(new_password)
        user.save()
        return user


class ProfileResetPasswordForm(forms.Form):
    email = forms.EmailField(label=u'电子邮件', error_messages={
        'invalid': '输入一个有效的 Email 地址。',
    })
