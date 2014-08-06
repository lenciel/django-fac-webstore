#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os

from django.core.urlresolvers import reverse
from apps.common.admin.datatables import DatatablesBuilder, DatatablesIdColumn, DatatablesTextColumn, DatatablesUserChoiceColumn, \
    DatatablesDateTimeColumn, DatatablesActionsColumn, \
    DatatablesColumnActionsRender, DatatablesIntegerColumn, DatatablesChoiceColumn
from apps.common.admin.forms import ModelDetail
from apps.order.models import Order

HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))

PERM_EDIT_ORDER = 'order.change_order'


class OrderDatatablesBuilder(DatatablesBuilder):
    id = DatatablesIdColumn()

    order_no = DatatablesTextColumn(label=u"订单号",
                                    search_expr="id",
                                    is_searchable=True,
                                    col_width="4%",
                                    render=lambda request, model, field_name:
        "<a href='#' data-url='%s'> %s </a>" % (reverse("admin:order:order_detail", kwargs={'pk': model.id}), model.order_no()), )

    sku_text_list = DatatablesTextColumn(label=u'sku',
                                         render=lambda request, model, field_name:
        "<ul>" + "".join(["<li>"+text+"</li>" for text in model.sku_text_list()]) + "</ul>"
    )

    amount = DatatablesIntegerColumn(label=u'总价')

    payment = DatatablesTextColumn(label=u'付款方式')

    status = DatatablesChoiceColumn(Order.ORDER_STATUS_CODES,
                                    label=u'状态',
                                    is_searchable=True)

    created = DatatablesDateTimeColumn(label=u'创建时间')

    owner = DatatablesUserChoiceColumn(label=u'用户')

    def actions_render(request, model, field_name):
        actions = []
        next_action = model.next_action_for_admin()
        if next_action:
            actions.append({'is_link': False, 'name': 'order_change_status', 'text': next_action['label'], 'icon': 'icon-money',
             'url': reverse('admin:order:order_change_status', kwargs={'pk': model.id, 'new_status': next_action['next']})})

        if model.status == Order.ORDER_STATUS_SHIPPED:
            # 已发货状态下额外显示录入快递信息的操作
            express_info_action = {'is_link': False, 'name': 'order_express_company', 'text': u'快递信息', 'icon': 'icon-envelope', 'handler_type': 'customize',
                                   'action_type': 'POST', 'extra': {'express': model.express_company},
                                   'url': reverse('admin:order:order_express_company', kwargs={'pk': model.id})}
            actions.append(express_info_action)
        order_history_action = {'is_link': True, 'name': 'order_history_list', 'text': u'订单历史', 'icon': 'icon-info',
                                'url': reverse('admin:order:order_history_list', kwargs={'pk': model.id})}
        actions.append(order_history_action)
        return DatatablesColumnActionsRender(actions=actions, action_permission=PERM_EDIT_ORDER).render(request, model, field_name)

    _actions = DatatablesActionsColumn(render=actions_render)


class OrderHistoryDatatablesBuilder(DatatablesBuilder):
    id = DatatablesIdColumn()

    order_no = DatatablesTextColumn(label=u"订单号",
                                    render=lambda request, model, field_name: model.order.order_no(),
                                    col_width="4%")

    status = DatatablesChoiceColumn(Order.ORDER_STATUS_CODES,
                                    label=u'状态')

    creator = DatatablesTextColumn(label=u'创建人')

    created = DatatablesDateTimeColumn(label=u'创建时间')


class OrderDetail(ModelDetail):
    @staticmethod
    def get_skus_display(model, skus):
        return skus.all()

    class Meta:
        model = Order
        excludes = ('is_active',)
        prefetch_fields = ('skus',)
