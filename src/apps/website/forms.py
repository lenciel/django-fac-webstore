#!/usr/bin/env python
# -*- coding: utf-8 -*-
from captcha.fields import CaptchaField

from django import forms
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.template import loader
from django.utils.http import int_to_base36
from apps.customer.models import Customer


class CustomerRegisterForm(forms.Form):
    name = forms.CharField(label=u'用户名',
                           max_length=30,
                           help_text=u'必填. 不能超过30个字符.')

    email = forms.EmailField(label=u'电子邮件',
                             max_length=254,
                             help_text=u'必填.')

    password1 = forms.CharField(label=u'密码',
                                widget=forms.PasswordInput,
                                help_text=u'必填.')
    password2 = forms.CharField(label=u'再次输入密码',
                                widget=forms.PasswordInput,
                                help_text=u'必填. 请再次输入密码以确认.')

    captcha = CaptchaField(label=u'验证码')

    def __init__(self, *args, **kwargs):
        super(CustomerRegisterForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = "required form-control"
        self.fields['email'].widget.attrs['class'] = "required form-control email"
        self.fields['password1'].widget.attrs['class'] = "required form-control"
        self.fields['password2'].widget.attrs['class'] = "required form-control"
        self.fields['captcha'].widget.attrs['class'] = "required form-control"

    def clean_email(self):
        UserModel = get_user_model()
        email = self.cleaned_data['email']
        users_cache = UserModel._default_manager.filter(email__iexact=email)
        if users_cache:
            raise forms.ValidationError(u'邮箱已被注册')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(u'两次输入的密码不匹配')
        return password2

    def send_email(self, request, user,
                   subject_template_name='website/account/sign_up_subject.txt',
                   email_template_name='website/account/sign_up_email.html',
                   token_generator=default_token_generator):
        from django.core.mail import send_mail
        site_name = settings.SITE_NAME
        domain = site_name
        c = {
            'email': user.email,
            'domain': domain,
            'site_name': site_name,
            'uid': int_to_base36(user.pk),
            'user': user,
            'token': token_generator.make_token(user),
            'protocol': request.is_secure() and 'https' or 'http',
        }
        subject = loader.render_to_string(subject_template_name, c)
        email = loader.render_to_string(email_template_name, c)
        # Email subject不换行
        subject = settings.EMAIL_SUBJECT_PREFIX + ' ' + ''.join(subject.splitlines())
        send_mail(subject, email, None, [user.email])

    def save(self, request):
        new_user = Customer.objects.create(
            is_active=False,
            name=self.cleaned_data['name'],
            email=self.cleaned_data['email'])
        new_user.set_password(self.cleaned_data['password1'])
        new_user.save()
        self.send_email(request=request, user=new_user)
        return new_user


class LoginForm(forms.Form):
    name = forms.CharField(label=u'账号', max_length=30,
        help_text=u'必填.')

    password = forms.CharField(label=u'密码',
        widget=forms.PasswordInput,
        help_text=u'必填.')

    keep_login = forms.BooleanField(label=u'保持15天在线', required=False)

    def clean_password(self):
        name = self.cleaned_data.get('name')
        password = self.cleaned_data.get('password')
        user = auth.authenticate(email=name, password=password)
        if not user:
            raise forms.ValidationError(u'账号或密码错误')
        else:
            self.auth_user = user
        return password