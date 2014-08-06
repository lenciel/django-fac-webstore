#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from django.test import TestCase
from django.test.utils import setup_test_environment
import os
from apps.order.models import Order

# test it with below command
#     ./manage.py jtest order --settings=settings.test --verbosity 0

setup_test_environment()

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


class BaseTestCase(TestCase):

    def setUp(self):
        self.order1 = Order.objects.get(id=1)
        self.maxDiff = 10240

    def tearDown(self):
        pass


class OrderTest(BaseTestCase):
    fixtures = ['test_product_data.json', 'test_customer_data.json', 'test_order_data.json']

    def test_sku_text_list(self):
        expect = ["(product1 red x small) 240.00 x 1 = 240.00",
                  "(product1 big x red) 200.00 x 2 = 400.00"]
        self.assertEqual(expect, self.order1.sku_text_list())
