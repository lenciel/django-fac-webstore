#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from apps.order.models import Order

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


class MyOrders(object):
    def __init__(self, user):
        self.user = user
        queryset = Order.objects.filter(owner=user).prefetch_related('skus')
        self.orders = {}
        self.all = []
        self.group(queryset)

    def group(self, queryset):
        for o in queryset:
            summary = OrderSummary(o)
            self.all.append(summary)
            self.orders.setdefault(summary.status, []).append(summary)

    def not_paid(self):
        return self.get_by_status(Order.ORDER_STATUS_DRAFT)

    def not_confirmed(self):
        return self.get_by_status(Order.ORDER_STATUS_SHIPPED)

    def uncompleted(self):
        return self.exclude([Order.ORDER_STATUS_CANCEL, Order.ORDER_STATUS_COMPLETED])

    def not_paid_count(self):
        return len(self.not_paid())

    def not_confirmed_count(self):
        return len(self.not_confirmed())

    def uncompleted_count(self):
        return len(self.uncompleted())

    def exclude(self, status):
        """
        Returns orders exclude that status in status
        """
        return [o for o in self.all if o.status not in set(status)]

    def get_by_status(self, status):
        return self.orders.get(status, [])


class OrderSummary(object):
    def __init__(self, order):
        skus = order.skus.all()
        self.title_img_url = skus[0].product.title_image_url()
        self.id = order.id
        self.seq = order.order_no()
        self.products = dict((s.product.id, s.product.name) for s in skus)
        self.amount = order.amount
        self.updated = order.updated
        self.status = order.status
        self.status_text = Order.ORDER_STATUS_CODES[(order.status + 1)][1]
        self.action = order.next_action_for_customer()
        self.cancel = order.cancel_action()