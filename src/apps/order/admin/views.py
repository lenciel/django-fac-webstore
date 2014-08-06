#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
from django.core.urlresolvers import reverse
from apps.common.admin.views import NavigationHomeMixin, ModelAwareMixin, DatatablesBuilderMixin, AjaxListView,\
    AjaxDatatablesView, AjaxSimpleUpdateView, PermissionRequiredMixin, ModelDetailView
from apps.order.models import  Order, OrderHistory

from .forms import OrderDatatablesBuilder, OrderHistoryDatatablesBuilder, PERM_EDIT_ORDER, OrderDetail


HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class OrderPermissionMixin(PermissionRequiredMixin):
    permission_required = PERM_EDIT_ORDER


class OrderListView(NavigationHomeMixin, ModelAwareMixin, DatatablesBuilderMixin, AjaxListView):
    model = Order
    queryset = Order.objects.get_empty_query_set()
    datatables_builder_class = OrderDatatablesBuilder
    model_name = 'order'
    template_name = 'order/admin/order.list.inc.html'


class OrderListDatatablesView(AjaxDatatablesView):
    model = Order
    datatables_builder_class = OrderListView.datatables_builder_class
    queryset = Order.objects.prefetch_related()
    template_name = 'order/admin/order.list.inc.html'


class OrderListByStatusView(NavigationHomeMixin, ModelAwareMixin, DatatablesBuilderMixin, AjaxListView):
    model = Order
    queryset = Order.objects.get_empty_query_set()
    datatables_builder_class = OrderDatatablesBuilder
    model_name = 'order_status'

    def get_datatables_list_url(self):
        return reverse("admin:order:order_list_by_status.datatables", kwargs={'status': self.kwargs['status']})

    def get_list_url(self):
        return reverse("admin:order:order_list_by_status", kwargs={'status': self.kwargs['status']})

    def get_model_name(self):
        return "order_by_status_%s" % self.kwargs['status']


class OrderListByStatusDatatablesView(AjaxDatatablesView):
    model = Order
    datatables_builder_class = OrderListByStatusView.datatables_builder_class

    def get_queryset(self):
        return Order.objects.prefetch_related().filter(status=int(self.kwargs['status']))


class OrderChangeStatusView(OrderPermissionMixin, AjaxSimpleUpdateView):
    model = Order

    def update(self, order):
        new_status = int(self.kwargs['new_status'])
        order.set_status(new_status, self.request.user)
        order.save()


class OrderExpressCompanyView(AjaxSimpleUpdateView):
    model = Order

    def update(self, obj):
        obj.express_company = self.request.POST['express']
        obj.save()


class OrderHistoryListView(ModelAwareMixin, DatatablesBuilderMixin, AjaxListView):
    model = OrderHistory
    datatables_builder_class = OrderHistoryDatatablesBuilder
    queryset = OrderHistory.objects.get_empty_query_set()
    model_name = "order"

    def get_datatables_list_url(self):
        pk = self.kwargs.get('pk')
        return reverse('admin:order:order_history_list.datatables', kwargs={'pk': pk})


class OrderHistoryListDatatablesView(AjaxDatatablesView):
    model = OrderHistory
    datatables_builder_class = OrderHistoryListView.datatables_builder_class

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return self.model.objects.filter(order=pk)


class OrderDetailView(ModelDetailView):
    model_detail_class = OrderDetail
    model = model_detail_class.Meta.model