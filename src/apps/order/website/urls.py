#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views


urlpatterns = patterns('',
    url(r'^builder/product/$', views.OrderBuilderProductView.as_view(), name='order_builder.product'),
    url(r'^builder/cart/(?P<cart>\d+)$', views.OrderBuilderCartView.as_view(), name='order_builder.cart'),
    url(r'^list$', views.OrderListView.as_view(), name='order_list'),
    url(r'^(?P<pk>\d+)/change_status/(?P<new_status>-?\d+)', views.OrderChangeStatusView.as_view(), name='order_change_status'),
    url(r'^(?P<pk>\d+)/detail$', views.OrderDetailView.as_view(), name='order_detail'),
    url(r'^confirm$', views.OrderPaymentConfirmView.as_view(), name='payment_confirm'),
)

urlpatterns += patterns('',
    url(r'^shipaddress/list$', views.AjaxShipAddressListView.as_view(), name='shipaddress_list'),
    url(r'^shipaddress/update$', views.AjaxShipAddressUpdateView.as_view(), name='shipaddress_update'),
    url(r'^shipaddress/(?P<pk>\d+)/delete$', views.AjaxShipAddressDeleteView.as_view(), name='shipaddress_delete'),
)
