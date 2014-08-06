#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import os

from django.utils.safestring import SafeString
from django.views.generic import DetailView
from apps.common.website.views import StaffRequiredMixin

from apps.product.models import Product


HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product/website/product.detail.v2.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.active_objects.select_related("category", "provider").\
            prefetch_related("attribute_options__attribute", 'detail_images__image', 'images__image', 'samplecases')

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        return self.get_queryset().get(pk=pk, is_published=True)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProductDetailView, self).get_context_data(**kwargs) # Add in a QuerySet of all the books
        attribute_options, skus = self.object.get_options_and_skus()
        context['attribute_options'] = attribute_options
        context['skus_json'] = SafeString(json.dumps(skus))

        return context


class ProductPreviewView(StaffRequiredMixin, ProductDetailView):
    model = Product
    template_name = 'product/website/product.detail.v2.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        return self.get_queryset().get(pk=pk)

    def get_context_data(self, **kwargs):
        context = super(ProductPreviewView, self).get_context_data(**kwargs)
        context['is_preview'] = True
        return context