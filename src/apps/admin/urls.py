#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf import settings

from django.conf.urls import patterns, url, include


urlpatterns = patterns('',
    url(r'^$', 'apps.admin.views.home', name='admin_home'),
    url(r'^dashboard$', 'apps.admin.views.dashboard'),
    url(r'^foundation/', include('apps.foundation.urls', namespace='foundation')),
    url(r'^account/', include('apps.account.urls', namespace='account')),
    url(r'^product/', include('apps.product.admin.urls', namespace='product')),
    url(r'^customer/', include('apps.customer.admin.urls', namespace='customer')),
    url(r'^order/', include('apps.order.admin.urls', namespace='order')),
    url(r'^cms/', include('apps.cms.admin.urls', namespace='cms')),
)


if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^loaddata/(?P<filename>.*)', 'apps.admin.views.loaddata'),
    )
