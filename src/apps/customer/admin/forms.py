#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os

from django.core.urlresolvers import reverse
from apps.common.admin.datatables import DatatablesBuilder, DatatablesIdColumn, DatatablesTextColumn, \
    DatatablesDateTimeColumn, DatatablesBooleanColumn, DatatablesActionsColumn, \
    DatatablesColumnActionsRender

HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))

PERM_EDIT_CUSTOMER = 'account.change_customer'


class CustomerDatatablesBuilder(DatatablesBuilder):

    id = DatatablesIdColumn()

    email = DatatablesTextColumn(label=u'账号',
                                 is_searchable=True)

    name = DatatablesTextColumn(label=u'名称',
                                is_searchable=True)

    is_active = DatatablesBooleanColumn((('', u'全部'), (1, u'激活'), (0, u'锁定')),
                                        label='状态',
                                        is_searchable=True,
                                        col_width='7%',
                                        render=(lambda request, model, field_name:
                                                u'<span class="label label-info"> 启用 </span>' if model.is_active else
                                                u'<span class="label label-warning"> 禁用 </span>'))

    date_joined = DatatablesDateTimeColumn(label=u'创建时间')

    def actions_render(request, model, field_name):
        if model.is_active:
            actions = [{'is_link': False, 'name': 'lock', 'text': u'锁定',
                        'icon': 'icon-lock', 'url_name': 'admin:account:user_lock'},
                       {'is_link': False, 'name': 'password_reset', 'text': u'重置密码',
                        'icon': 'icon-edit', 'url': reverse('admin:account:password_reset'), 'action_type': 'POST',
                        'extra': {'email': model.email}}]
        else:
            actions = [{'is_link': False, 'name': 'unlock', 'text': u'解锁',
                        'icon': 'icon-unlock', 'url_name': 'admin:account:user_unlock'}]
        return DatatablesColumnActionsRender(actions=actions, action_permission=PERM_EDIT_CUSTOMER).render(request, model, field_name)

    _actions = DatatablesActionsColumn(render=actions_render)
