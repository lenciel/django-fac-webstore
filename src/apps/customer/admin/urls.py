#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^list$', views.CustomerListView.as_view(), name='customer_list'),
    url(r'^list.datatables$', views.CustomerListDatatablesView.as_view(), name='customer_list.datatables'),
    url(r'^(?P<pk>\d+)/lock', views.CustomerLockView.as_view(), name='customer_lock'),
    url(r'^(?P<pk>\d+)/unlock', views.CustomerUnlockView.as_view(), name='customer_unlock'),
)
