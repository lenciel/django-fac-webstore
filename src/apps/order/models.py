#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from django.db.models import signals
from django.dispatch import Signal, receiver
import os

from django.db import models
from django.contrib.auth import get_user_model
from apps.customer.models import Address, Customer
from apps.product.models import ProductSku

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


class Invoice(Address):
    content = models.CharField(verbose_name=u'发票内容',
                               max_length=128)

    def __unicode__(self):
        return "%d" % self.id

    class Meta:
        verbose_name = u'订单发票'
        verbose_name_plural = verbose_name


class OrderSku(models.Model):
    order = models.ForeignKey("Order",
                              verbose_name=u'订单')

    sku = models.ForeignKey(ProductSku,
                            verbose_name=u'商品sku')

    quantity = models.PositiveIntegerField(verbose_name=u'数量')

    price = models.DecimalField(max_digits=16,
                                decimal_places=2,
                                verbose_name=u'单价',
                                default=0.0)

    amount = models.DecimalField(max_digits=16,
                                 decimal_places=2,
                                 verbose_name=u'总价',
                                 default=0.0)

    notes = models.CharField(verbose_name=u'备注',
                             max_length=128,
                             default="",
                             blank=True)

    def save(self, **kwargs):
        self.amount = self.quantity * self.price
        super(OrderSku, self).save(self, **kwargs)

    def display_text(self):
        return u"(%s) %.2f x %d = %.2f" % (self.sku.display_text(), float(self.price), self.quantity, float(self.amount))

    def __unicode__(self):
        return u"%s-%s" % (unicode(self.order), unicode(self.sku))

    class Meta:
        verbose_name = u'订单sku'
        verbose_name_plural = verbose_name


post_order_status_changed = Signal(providing_args=["new_status", "actor"])


class Order(models.Model):
    skus = models.ManyToManyField(ProductSku,
                                  through="OrderSku",
                                  verbose_name=u'商品sku集')

    amount = models.DecimalField(max_digits=16,
                                 decimal_places=2,
                                 verbose_name=u'总价',
                                 default=0.0)

    # 因为发货地址可能在订单后会改变, 所有这里没有添加引用,而是存放地址快照.
    ship_address = models.CharField(verbose_name=u'送货地址',
                                    max_length=255,
                                    default="",
                                    blank=True)

    express_company = models.CharField(default='',
                                       blank=True,
                                       verbose_name=u'快递公司和快递号',
                                       max_length=128)

    # TODO: should refer to real payment instead of a string
    payment = models.CharField(verbose_name=u'付款方式',
                               max_length=100,
                               default="",
                               blank=True)

    invoice = models.OneToOneField(Invoice,
                                   verbose_name=u'发票',
                                   null=True,
                                   blank=True,)

    created = models.DateTimeField(verbose_name=u'创建时间',
                                   auto_now_add=True)

    updated = models.DateTimeField(verbose_name=u'更新时间',
                                   auto_now=True)

    owner = models.ForeignKey(Customer,
                              verbose_name=u'消费用户')

    notes = models.CharField(verbose_name=u'留言',
                             max_length=256,
                             default="",
                             blank=True)

    ORDER_STATUS_CANCEL = -1
    ORDER_STATUS_DRAFT = 0
    ORDER_STATUS_PAID = 1
    ORDER_STATUS_SHIPPED = 2
    ORDER_STATUS_COMPLETED = 3
    ORDER_STATUS_CODES = (
        (ORDER_STATUS_CANCEL, u'已撤销'),
        (ORDER_STATUS_DRAFT, u'未支付'),
        (ORDER_STATUS_PAID, u'已付款'),
        (ORDER_STATUS_SHIPPED, u'已发货'),
        (ORDER_STATUS_COMPLETED, u'已完成'),
    )
    # the action transitions for customer
    ORDER_STATUS_CUSTOMER_NEXT_ACTIONS = {
        ORDER_STATUS_CANCEL: {},
        ORDER_STATUS_DRAFT: {'next': ORDER_STATUS_PAID, 'label': u'去付款', 'active': True},
        ORDER_STATUS_PAID: {'next': ORDER_STATUS_SHIPPED, 'label': u'等待发货', 'active': False},
        ORDER_STATUS_SHIPPED: {'next': ORDER_STATUS_COMPLETED, 'label': u'确认收货', 'active': True},
        ORDER_STATUS_COMPLETED: {},
    }
    # the action transitions for admin
    ORDER_STATUS_ADMIN_NEXT_ACTIONS = {
        ORDER_STATUS_CANCEL: {},
        ORDER_STATUS_DRAFT: {},
        ORDER_STATUS_PAID: {'next': ORDER_STATUS_SHIPPED, 'label': u'发货'},
        ORDER_STATUS_SHIPPED: {},
        ORDER_STATUS_COMPLETED: {},
    }

    # TODO: how about "return"?
    status = models.IntegerField(default=ORDER_STATUS_DRAFT,
                                 choices=ORDER_STATUS_CODES,
                                 verbose_name=u'状态')

    def next_action_for_customer(self):
        return self.ORDER_STATUS_CUSTOMER_NEXT_ACTIONS.get(self.status)

    def next_action_for_admin(self):
        return self.ORDER_STATUS_ADMIN_NEXT_ACTIONS.get(self.status)

    def cancel_action(self):
        return {'next': self.ORDER_STATUS_CANCEL,
                'label': u'取消订单',
                'active': True} if self.status == self.ORDER_STATUS_DRAFT else {}

    def sku_text_list(self):
        return [order_sku.display_text() for order_sku in self.ordersku_set.all()]

    def order_no(self):
        return "%.7d" % self.id

    def is_complete(self):
        return self.status in {self.ORDER_STATUS_CANCEL, self.ORDER_STATUS_COMPLETED}

    def set_status(self, new_status, actor):
        # A order could be set to cancel status only when the order is not paid yet.
        if new_status == Order.ORDER_STATUS_CANCEL and self.status != self.ORDER_STATUS_DRAFT:
            return False
        # check the new status is transited with given rules
        next_action = self.next_action_for_customer()
        if actor.is_staff:
            next_action = self.next_action_for_admin()
        if not next_action or next_action['next'] != new_status:
            return False

        if self.status != new_status:
            self.status = new_status
            post_order_status_changed.send(Order, instance=self, new_status=new_status, actor=actor)
            return True
        return False

    def __unicode__(self):
        return self.order_no()

    class Meta:
        verbose_name = u'订单'
        verbose_name_plural = verbose_name
        ordering = ('-created',)


class OrderHistory(models.Model):
    order = models.ForeignKey(Order,
                              verbose_name=u'订单')

    created = models.DateTimeField(verbose_name=u'创建时间',
                                   auto_now_add=True)

    creator = models.ForeignKey(get_user_model(),
                                verbose_name=u'创建者', )

    status = models.IntegerField(default=Order.ORDER_STATUS_DRAFT,
                                 choices=Order.ORDER_STATUS_CODES,
                                 verbose_name=u'状态')

    def __unicode__(self):
        return "%s-%s" % (unicode(self.order), dict(Order.ORDER_STATUS_CODES)[self.status])

    class Meta:
        verbose_name = u'订单历史'
        verbose_name_plural = verbose_name
        ordering = ('-created',)
        permissions = (('view_order', u'查看订单'),)


@receiver(post_order_status_changed, sender=Order)
def handle_order_status_changed(sender, **kwargs):
    OrderHistory.objects.create(order=kwargs['instance'], status=kwargs['new_status'], creator=kwargs['actor'])


@receiver(signals.post_save, sender=Order)
def handle_new_order(sender, **kwargs):
    order = kwargs['instance']
    is_new = kwargs['created']
    if is_new:
        OrderHistory.objects.create(order=order, status=order.status, creator=order.owner)
