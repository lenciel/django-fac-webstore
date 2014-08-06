#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from django.test import TestCase
from django.test.utils import setup_test_environment
import os

# test it with below command
#     ./manage.py jtest order --settings=settings.test --verbosity 0

setup_test_environment()

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


class BaseTestCase(TestCase):

    def setUp(self):
        self.maxDiff = 10240

    def tearDown(self):
        pass
