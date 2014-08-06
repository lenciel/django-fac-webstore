#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
from django.contrib import auth
from apps.common.admin.views import NavigationHomeMixin, ModelAwareMixin, DatatablesBuilderMixin, AjaxListView,\
    AjaxDatatablesView, AjaxSimpleUpdateView, PermissionRequiredMixin
from apps.customer.models import Customer

from .forms import CustomerDatatablesBuilder, PERM_EDIT_CUSTOMER


HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class CustomerPermissionMixin(PermissionRequiredMixin):
    permission_required = PERM_EDIT_CUSTOMER


class CustomerListView(NavigationHomeMixin, ModelAwareMixin, DatatablesBuilderMixin, AjaxListView):
    model = Customer
    queryset = auth.get_user_model().objects.get_empty_query_set()
    datatables_builder_class = CustomerDatatablesBuilder
    model_name = 'customer'


class CustomerListDatatablesView(AjaxDatatablesView):
    model = Customer
    datatables_builder_class = CustomerListView.datatables_builder_class
    queryset = Customer.objects.prefetch_related().order_by('-date_joined')


class CustomerLockView(CustomerPermissionMixin, AjaxSimpleUpdateView):
    model = Customer

    def update(self, user):
        user.is_active = False
        user.save()


class CustomerUnlockView(CustomerPermissionMixin, AjaxSimpleUpdateView):
    model = auth.get_user_model()

    def update(self, user):
        user.is_active = True
        user.save()
