#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views


urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)/$', views.ProductDetailView.as_view(), name='product_detail'),
    url(r'^(?P<pk>\d+)/preview$', views.ProductPreviewView.as_view(), name='product_preview'),
)
