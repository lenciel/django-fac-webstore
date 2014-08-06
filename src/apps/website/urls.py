#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    url(r'^$', 'apps.website.views.index', name='index'),
    url(r'^login$', 'apps.website.views.login', name='login'),
    url(r'^logout$', 'apps.website.views.logout', name='logout'),
    url(r'^sign_up$', 'apps.website.views.sign_up', name='sign_up'),
    url(r'^to_email_confirm$', 'apps.website.views.to_email_confirm', name='to_email_confirm'),
    url(r'^legal$', 'apps.website.views.legal', name='legal'),
    url(r'^privacy$', 'apps.website.views.privacy', name='privacy'),
    url(r'^email_confirm/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 'apps.website.views.email_confirm', name='email_confirm'),
)

urlpatterns += patterns('',
    url(r'^product/', include('apps.product.website.urls', namespace='product')),
    url(r'^customer/', include('apps.customer.website.urls', namespace='customer')),
    url(r'^order/', include('apps.order.website.urls', namespace='order')),
    url(r'^payment/', include('apps.payment.website.urls', namespace='payment')),
    url(r'^cms/', include('apps.cms.website.urls', namespace='cms')),
)