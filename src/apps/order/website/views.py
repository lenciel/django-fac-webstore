#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import json

import logging
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.safestring import SafeString
from django.views.generic import ListView, CreateView, View
from django.views.generic.base import TemplateResponseMixin
from django.http import HttpResponseRedirect, QueryDict
import os
from apps.common import exceptions
from apps.common.admin.views import AjaxSimpleUpdateView, ModelDetailView, HttpResponseJson
from apps.common.website.views import LoginRequiredMixin
from apps.customer.models import ShipAddress
from apps.customer.website.forms import ShipAddressForm
from apps.order.models import Order
from apps.order.website.forms import OrderDetail, OrderBuilderProductParamForm, \
    InvoiceForm, OrderForm, OrderSkuForm
from apps.order.website.models import MyOrders
from utils.db.queryutil import get_object_or_none


HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class AjaxShipAddressListView(LoginRequiredMixin, ListView):
    template_name = "order/website/order.shipaddress.inc.html"
    model = ShipAddress

    def get_queryset(self):
        return self.request.user.customer.ship_addresses.all()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(AjaxShipAddressListView, self).get_context_data(**kwargs)
        ship_addresses = []
        selected_address_id = self.request.GET.get('selected')
        for address in self.get_queryset():
            if address.is_default:
                selected_address_id = selected_address_id or address.id
            ship_addresses.append({"id": address.id,
                                   "is_default": address.is_default,
                                   "display_text": address.display_text(),
                                   "value_json": SafeString(json.dumps(address.to_json()))})
        context['ship_addresses'] = ship_addresses
        context['selected_address_id'] = selected_address_id

        return context


class AjaxShipAddressUpdateView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        pk = request.POST.get('id', None)
        ship_address = None
        if pk:
            ship_address = get_object_or_none(ShipAddress, pk=pk)
            if not ship_address:
                raise exceptions.AjaxRecordNotExist()

        form_instance = ShipAddressForm(self.request.user.customer, self.request.POST, self.request.FILES, instance=ship_address)
        if form_instance.is_valid():
            form_instance.save()
            result = exceptions.build_success_response_result()
        else:
            raise exceptions.AjaxValidateFormFailed(errors=form_instance.errors)
        return HttpResponseJson(result)


class AjaxShipAddressDeleteView(LoginRequiredMixin, View):
    http_method_names = ['post']
    model = ShipAddress

    def post(self, request, *args, **kwargs):
        ship_address = ShipAddress.objects.filter(pk=self.kwargs['pk'], owner=self.request.user.customer)
        if not ship_address:
            raise exceptions.AjaxRecordNotExist()
        ship_address.delete()
        return HttpResponseJson(exceptions.build_success_response_result())


class OrderBuilderProductView(LoginRequiredMixin, TemplateResponseMixin, View):
    template_name = "order/website/order.builder.html"
    model = Order

    def get(self, request, *args, **kwargs):
        form = OrderBuilderProductParamForm(self.request.GET)
        if form.is_valid():
            context = self.get_context_data(**kwargs)
            sku = form.cleaned_data['sku_id']
            quantity = form.cleaned_data['quantity']
            context['sku_list'] = [{"sku": sku,
                                    "quantity": quantity,
                                    "amount": quantity * float(sku.price)}]
            return self.render_to_response(context)
        else:
            return HttpResponseRedirect(reverse('website:home'))

    @transaction.commit_on_success
    def post(self, request, *args, **kwargs):
        invoice_form = InvoiceForm(request.POST, prefix="invoice")
        if not invoice_form.is_valid():
            errors = {}
            # prefix the key with "invoice" to let jquery validate lookup it correctly.
            for key, value in invoice_form.errors.items():
                errors["invoice-"+key] = value
            raise exceptions.AjaxValidateFormFailed(errors=errors)
        invoice = invoice_form.save()

        order_form = OrderForm(request.user.customer, invoice, request.POST)
        if not order_form.is_valid():
            raise exceptions.AjaxValidateFormFailed(errors=order_form.errors)
        order = order_form.save()

        self.handle_sku(request, order)
        ret = copy.deepcopy(exceptions.build_success_response_result())
        ret['redirect_url'] = reverse("website:order:payment_confirm")
        return HttpResponseJson(ret)

    def handle_sku(self, request, order):
        # the sku id is composed with given name like "sku_100"
        # the quantity is composed with given name like "quantity_100_2"
        sku_ids = request.POST.getlist('sku_id', [])
        amount = 0
        for sku_id in sku_ids:
            q = QueryDict('', mutable=True)
            q['sku'] = int(sku_id)
            q['quantity'] = int(request.POST.get('quantity_' + sku_id))
            q['notes'] = request.POST.get('notes_' + sku_id)
            q['price'] = request.POST.get('price_' + sku_id)
            sku_form = OrderSkuForm(order, q)
            if not sku_form.is_valid():
                raise exceptions.AjaxValidateFormFailed(errors=sku_form.errors)
            order_sku = sku_form.save()
            amount += float(order_sku.amount)
        Order.objects.filter(id=order.id).update(amount=amount)

    def get_context_data(self, **kwargs):
        context = {}
        ship_addresses = []
        selected_address_id = None
        for address in self.request.user.customer.ship_addresses.all():
            if address.is_default:
                selected_address_id = address.id
            ship_addresses.append({"id": address.id,
                                   "is_default": address.is_default,
                                   "display_text": address.display_text(),
                                   "value_json": SafeString(json.dumps(address.to_json()))})
        context['ship_addresses'] = ship_addresses
        context['selected_address_id'] = selected_address_id
        return context


class OrderBuilderCartView(LoginRequiredMixin, CreateView):
    template_name = "order/website/order.builder.html"
    model = Order

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(OrderBuilderCartView, self).get_context_data(**kwargs)
        context['ship_addresses'] = self.request.user.customer.ship_addresses
        return context


class OrderListView(LoginRequiredMixin, View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        my_orders = MyOrders(self.request.user)
        return render_to_response('customer/website/customer.order.html',
                                  locals(),
                                  context_instance=RequestContext(request))


class OrderChangeStatusView(AjaxSimpleUpdateView):
    model = Order

    def update(self, order):
        new_status = int(self.kwargs['new_status'])
        if not order.owner.id == self.request.user.id or new_status == Order.ORDER_STATUS_PAID:
            return u'非法操作'
        if not order.set_status(new_status, self.request.user):
            return u'非法操作'
        order.save()


class OrderDetailView(ModelDetailView):
    model_detail_class = OrderDetail
    model = model_detail_class.Meta.model


class OrderPaymentConfirmView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order/website/payment.confirm.html'

    def get_queryset(self):
        # TODO 需要确定显示有效的待支付订单的过滤条件
        return Order.objects.filter(owner=self.request.user.customer).filter(status=Order.ORDER_STATUS_DRAFT)

    def get_context_data(self, **kwargs):
        context = super(OrderPaymentConfirmView, self).get_context_data(**kwargs)
        context['total'] = self.get_queryset().aggregate(Sum('amount'))['amount__sum']
        return context

    def post(self, request, *args, **kwargs):
        self.get_queryset().update(status=Order.ORDER_STATUS_PAID)
        return HttpResponseRedirect(reverse("website:payment:payment_feedback"))