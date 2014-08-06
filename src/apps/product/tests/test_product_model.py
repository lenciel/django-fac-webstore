#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import OrderedDict
import logging

from django.test import TestCase
from django.test.utils import setup_test_environment
import os
from apps.product.models import Product

# test it with below command
#     ./manage.py jtest product --settings=settings.test --verbosity 0

setup_test_environment()

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


class BaseTestCase(TestCase):

    def setUp(self):
        self.product1 = Product.objects.get(id=1)
        self.maxDiff = 10240

    def tearDown(self):
        pass


class ProductTest(BaseTestCase):
    fixtures = ['test_product_data.json']

    def test_get_options_and_prices(self):
        expect_options = OrderedDict([(u'size', [{'exclude_option_ids': set([]), 'paired_option_ids': set([12, 20, 21]), 'id': 12, 'value': u'big'},
                                                 {'exclude_option_ids': set([]), 'paired_option_ids': set([11, 21]), 'id': 11, 'value': u'medium'},
                                                 {'exclude_option_ids': set([]), 'paired_option_ids': set([10, 20]), 'id': 10, 'value': u'small'}]),
                                      (u'color', [{'exclude_option_ids': set([]), 'paired_option_ids': set([12, 10, 20]), 'id': 20, 'value': u'red'},
                                                  {'exclude_option_ids': set([]), 'paired_option_ids': set([11, 12, 21]), 'id': 21, 'value': u'white'}])])
        expect_prices = {u'12,20': {'is_outofstock': False, 'price': 2.4, 'sku_id': 2},
                         u'11,21': {'is_outofstock': False, 'price': 3.3, 'sku_id': 3},
                         u'10,20': {'is_outofstock': False, 'price': 2.2, 'sku_id': 1},
                         u'12,21': {'is_outofstock': False, 'price': 3.4, 'sku_id': 4}}
        options, prices = self.product1.get_options_and_skus()
        self.assertEqual(expect_options, options)
        self.assertDictEqual(expect_prices, prices)
