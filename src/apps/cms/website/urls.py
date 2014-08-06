#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views


urlpatterns = patterns('',
    url(r'^article/(?P<pk>\d+)/$', views.ArticleDetailView.as_view(), name='article_detail'),
    url(r'^article/(?P<pk>\d+)/preview$', views.ArticlePreviewView.as_view(), name='article_preview'),
)
