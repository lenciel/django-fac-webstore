#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views


urlpatterns = patterns('',
    url(r'^article/list$', views.ArticleListView.as_view(), name='article_list'),
    url(r'^article/list.datatables$', views.ArticleListDatatablesView.as_view(), name='article_list.datatables'),
    url(r'^article/create$', views.ArticleCreateView.as_view(), name='article_create'),
    url(r'^article/(?P<pk>\d+)/edit$', views.ArticleEditView.as_view(), name='article_edit'),
    url(r'^article/(?P<pk>\d+)/delete$', views.ArticleDeleteView.as_view(), name='article_delete'),
    url(r'^article/(?P<pk>\d+)/publish$', views.ArticlePublishView.as_view(), name='article_publish'),
    url(r'^article/(?P<pk>\d+)/cancel', views.ArticleCancelView.as_view(), name='article_cancel'),
)
