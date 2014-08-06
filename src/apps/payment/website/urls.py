#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views


urlpatterns = patterns('',
    url(r'^feedback$', views.PaymentFeedbackView.as_view(), name='payment_feedback'),
)
