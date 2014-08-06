#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from django import forms
from django.db.models import F
import os
from django.core.urlresolvers import reverse
from apps.common.admin.datatables import DatatablesColumnActionsRender, DatatablesActionsColumn
from apps.common.admin.forms import ModelDetail
from apps.order.admin.forms import OrderDatatablesBuilder
from apps.order.models import Order, Invoice, OrderSku
from apps.product.models import ProductSku, Product


HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class CustomerOrderDatatablesBuilder(OrderDatatablesBuilder):

    def actions_render(request, model, field_name):
        actions = [{'is_link': True, 'name': 'order_detail', 'text': u'详情', 'icon': 'icon-eye-open',
                    'url': reverse('website:order:order_detail', kwargs={'pk': model.id})}]
        if model.status == Order.ORDER_STATUS_DRAFT:
            actions += [{'is_link': False, 'name': 'order_change_status', 'text': u'取消', 'icon': 'icon-lock',
                        'url': reverse('website:order:order_change_status', kwargs={'pk': model.id, 'new_status': Order.ORDER_STATUS_CANCEL})},
                       {'is_link': False, 'name': 'order_change_status', 'text': u'付款', 'icon': 'icon-lock',
                        'url': reverse('website:order:order_change_status', kwargs={'pk': model.id, 'new_status': Order.ORDER_STATUS_PAID})}]
            logger.debug(actions)
        elif model.status == Order.ORDER_STATUS_SHIPPED:
            actions += [{'is_link': False, 'name': 'order_change_status', 'text': u'完成', 'icon': 'icon-lock',
                        'url': reverse('website:order:order_change_status', kwargs={'pk': model.id, 'new_status': Order.ORDER_STATUS_COMPLETED})}]
        return DatatablesColumnActionsRender(actions=actions).render(request, model, field_name)

    _actions = DatatablesActionsColumn(render=actions_render)


class OrderDetail(ModelDetail):
    @staticmethod
    def get_skus_display(model, skus):
        return skus.all()

    class Meta:
        model = Order
        excludes = ('is_active',)
        prefetch_fields = ('skus',)


class OrderBuilderProductParamForm(forms.Form):

    quantity = forms.IntegerField(required=True)

    sku_id = forms.IntegerField(required=True)

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 1:
            raise forms.ValidationError(u'数量必须大于1')
        return quantity

    def clean_sku_id(self):
        try:
            sku = ProductSku.objects.get(id=self.cleaned_data['sku_id'])
        except ProductSku.DoesNotExist:
            raise forms.ValidationError(u'非法的产品编号')
        return sku

    class Meta:
        fields = ('quantity', 'sku_id')


class OrderSkuForm(forms.ModelForm):
    def __init__(self, order, *args, **kwargs):
        super(OrderSkuForm, self).__init__(*args, **kwargs)
        self.order = order

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 1:
            raise forms.ValidationError(u'数量必须大于1')
        return quantity

    def clean_price(self):
        price = self.cleaned_data['price']
        if price < 0:
            raise forms.ValidationError(u'不正确的商品价格')
        return price

    def clean(self):
        cleaned_data = super(OrderSkuForm, self).clean()
        if any(self.errors):
            # Don’t bother validating the formset unless each form is valid on its own
            return
        if cleaned_data['price'] != cleaned_data['sku'].price:
            raise forms.ValidationError(u'商品价格已经被管理员修改!')
        return cleaned_data

    def save(self, commit=False):
        order_sku = super(OrderSkuForm, self).save(commit)
        order_sku.order = self.order
        order_sku.save()
        Product.objects.filter(id=order_sku.sku.product.id).update(sale_volume=F("sale_volume")+1)
        return order_sku

    class Meta:
        fields = ('price', 'sku', 'quantity')
        model = OrderSku


class OrderForm(forms.ModelForm):

    def __init__(self, customer, invoice, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.customer = customer
        self.invoice = invoice

    def save(self, commit=False):
        order = super(OrderForm, self).save(commit)
        order.owner = self.customer
        order.invoice = self.invoice
        order.save()
        return order

    class Meta:
        model = Order
        fields = ('payment', 'ship_address', 'notes',)


class InvoiceForm(forms.ModelForm):

    class Meta:
        model = Invoice
        fields = ('content', 'receiver', 'address', 'address_province', 'address_city', 'address_district', 'mobile')

