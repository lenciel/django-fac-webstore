#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf import settings

from django.conf.urls import patterns, url
from apps.api import views


urlpatterns = patterns('',
)

if settings.DEBUG:
    # for the time being, wechat only is available for debug
    urlpatterns += patterns('',
        url(r'^wechat', views.WechatView.as_view(), name='wechat'),
    )
