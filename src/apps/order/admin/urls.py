#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^list$', views.OrderListView.as_view(), name='order_list'),
    url(r'^list.datatables$', views.OrderListDatatablesView.as_view(), name='order_list.datatables'),
    url(r'^list_by_status/(?P<status>-?\d+)$', views.OrderListByStatusView.as_view(), name='order_list_by_status'),
    url(r'^list_by_status.datatables/(?P<status>-?\d+)$', views.OrderListByStatusDatatablesView.as_view(), name='order_list_by_status.datatables'),

    url(r'^(?P<pk>\d+)$', views.OrderDetailView.as_view(), name='order_detail'),
    url(r'^(?P<pk>\d+)/change_status/(?P<new_status>\d+)$', views.OrderChangeStatusView.as_view(), name='order_change_status'),
    url(r'^(?P<pk>\d+)/express_company', views.OrderExpressCompanyView.as_view(), name='order_express_company'),
    url(r'^(?P<pk>\d+)/order_history_list$', views.OrderHistoryListView.as_view(), name='order_history_list'),
    url(r'^(?P<pk>\d+)/order_history_list.datatables$', views.OrderHistoryListDatatablesView.as_view(), name='order_history_list.datatables'),
)