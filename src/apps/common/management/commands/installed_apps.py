#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Show the installed apps
    """

    def handle(self, *args, **options):
        print ' '.join(settings.INSTALLED_APPS)
