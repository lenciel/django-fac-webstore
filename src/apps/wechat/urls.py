#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from apps.wechat import views


urlpatterns = patterns('',
                       url(r'^api$', views.WeChatApiView.as_view(), name='api'),
                       url(r'^bind$', views.WeChatBindView.as_view(), name='bind'),
                       url(r'^product/list$', views.WeChatProductList.as_view(), name='product_list'),
                       url(r'^product/search$', views.WeChatProductSearch.as_view(), name='product_search'),
                       url(r'^product/(?P<pk>\d+)$', views.WeChatProductDetailView.as_view(), name='product_detail'),
                       url(r'^$', views.WechatView.as_view(), name='home'),
)
