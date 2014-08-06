#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.http import base36_to_int
from apps.product.models import Product
from apps.website.forms import CustomerRegisterForm, LoginForm

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


def index(request):
    products = Product.active_objects.filter(is_published=True, is_pinned=False).order_by('-rating', '-updated').all()
    return TemplateResponse(request, 'website/index.html', locals())


def legal(request):
    return TemplateResponse(request, 'website/legal.inc.html')


def privacy(request):
    return TemplateResponse(request, 'website/privacy.inc.html')


def login(request):
    form = LoginForm()
    next = request.GET.get('next', 'customer/home')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            auth.login(request, form.auth_user)
            logger.info('Authenticate success for user ' + form.auth_user.email)
            if form.cleaned_data['keep_login']:
                request.session.set_expiry(settings.SESSION_COOKIE_AGE_15_DAY)
            if next:
                return HttpResponseRedirect(next)
            else:
                return HttpResponseRedirect(reverse('website:customer:customer_home'))

    form_action_url = reverse('website:login')
    if next:
        form_action_url = form_action_url + "?next="+next
    context = {'form': form, "form_action_url": form_action_url}

    return TemplateResponse(request, 'website/login.html', context)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('website:home'))


def sign_up(request):
    if request.method == "POST":
        form = CustomerRegisterForm(request.POST)
        if form.is_valid():
            form.save(request)
            return HttpResponseRedirect(reverse('website:to_email_confirm'))
    else:
        form = CustomerRegisterForm()
    context = {
        'form': form,
    }
    return TemplateResponse(request, 'website/account/sign_up.html', context)


def to_email_confirm(request):
    return TemplateResponse(request, 'website/account/to_email_confirm.html')


def email_confirm(request,
                  uidb36=None,
                  token=None,
                  token_generator=default_token_generator):
    UserModel = get_user_model()
    assert uidb36 is not None and token is not None
    try:
        uid_int = base36_to_int(uidb36)
        user = UserModel._default_manager.get(pk=uid_int)
    except (ValueError, OverflowError, UserModel.DoesNotExist):
        user = None
    if user and token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        valid_link = True
    else:
        valid_link = False
    context = {
        'valid_link': valid_link
    }
    return TemplateResponse(request, 'website/account/email_confirm_complete.html', context)