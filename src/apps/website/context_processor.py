#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf import settings


def ga_property_id(request):
    return {
        'ga_property_id': settings.GOOGLE_ANALYTICS_PROPERTY_ID,
        }