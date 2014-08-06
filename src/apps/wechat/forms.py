#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib

from django import forms
from django.conf import settings
from django.contrib import auth
from django.utils import timezone
from apps.wechat.models import WeChatUser

from apps.customer.models import Customer


class WeChatAccountBindForm(forms.ModelForm):
    """
    帐号绑定 form
    用于用户帐号和微信帐号的绑定
    """
    account = forms.CharField(label=u'账户名',
                              required=True,
                              error_messages={'required': u'账户名不能为空'})

    password = forms.CharField(label=u'密码',
                               required=True,
                               widget=forms.PasswordInput,
                               error_messages={'required': u'密码不能为空'})
    signature = forms.CharField(widget=forms.HiddenInput,
                                required=False)

    class Meta:
        model = WeChatUser
        fields = ('openid',)
        widgets = {'openid': forms.HiddenInput}

    def __init__(self, *args, **kwargs):
        super(WeChatAccountBindForm, self).__init__(*args, **kwargs)
        #signature used to verify open_id whether changed by user
        wechat_open_id = kwargs.get('initial', {}).get("openid", "")
        self.fields['signature'].initial = hashlib.sha1(wechat_open_id + settings.SECRET_KEY).hexdigest()
        self.user_id = None
        self.is_pre_wechat_user_exist = False

        # add custom error messages
        self.fields['openid'].error_messages = {'required': u'服务器错误'}

    def clean(self):
        cleaned_data = super(WeChatAccountBindForm, self).clean()
        if any(self.errors):
            # Don’t bother validating the formset unless each form is valid on its own
            return

        #verify signature
        signature = self.cleaned_data.get("signature")
        calc_signature = hashlib.sha1(self.cleaned_data.get("openid", "") + settings.SECRET_KEY).hexdigest()
        if signature != calc_signature:
            raise forms.ValidationError(u'签名不正确!')
        #verify auth info
        user = auth.authenticate(email=self.cleaned_data["account"],
                                 password=self.cleaned_data["password"])
        if user:
            self.user_id = user.id
        else:
            raise forms.ValidationError(u'用户名和密码错误!')
        return cleaned_data

    def save(self, commit=False):
        wechat_user = super(WeChatAccountBindForm, self).save(commit)
        wechat_user.customer = Customer.objects.get(id=self.user_id)
        try:
            pre_wechat_user = WeChatUser.objects.get(customer=self.user_id)
            pre_wechat_user.customer = wechat_user.customer
            pre_wechat_user.created_at = timezone.now()
            pre_wechat_user.save()
            self.is_pre_wechat_user_exist = True
        except WeChatUser.DoesNotExist:
            wechat_user.save()

        return wechat_user
