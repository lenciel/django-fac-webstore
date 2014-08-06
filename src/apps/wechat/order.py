#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import reverse
from django.dispatch import receiver
from django.db.models import signals
from apps.order.models import Order, post_order_status_changed
from apps.order.website.models import MyOrders
from apps.wechat.client import WeChatClient
from apps.wechat.menu import WeChatMenu
from apps.wechat.models import WeChatUser, logger

# 当订单状态变化时，通过微信通知客户
from apps.wechat.protocols import WeChatTextResponse, WeChatTextRequest, WeChatEventRequest
from apps.wechat.user_auth import WeChatUserAuth


def notify_user_when_order_status_created_or_changed(order, new_status):
    customer = order.owner.customer
    queryset = WeChatUser.objects.filter(customer__id=customer.id)
    if queryset:
        # notify user by WeChat
        openid = queryset[0].openid
        text = ''
        if new_status == Order.ORDER_STATUS_CANCEL:
            text = '您的订单已取消，欢迎再次光临'
        elif new_status == Order.ORDER_STATUS_DRAFT:
            text = ''
        elif new_status == Order.ORDER_STATUS_PAID:
            text = '您的订单以支付，请等待发货'
        elif new_status == Order.ORDER_STATUS_SHIPPED:
            text = '您的订单已发货，请等待收货'
        elif new_status == Order.ORDER_STATUS_COMPLETED:
            text = '您的订单已完成，欢迎再次光临'

        if text:
            WeChatClient.post_text_message(openid, text)


@receiver(post_order_status_changed, sender=Order)
def notify_user_when_order_status_changed(sender, **kwargs):
    try:
        order = kwargs['instance']
        new_status = kwargs['new_status']
        notify_user_when_order_status_created_or_changed(order, new_status)
    except Exception, e:
        logger.error('notify user when order status changed failed: {0}', e.message)


@receiver(signals.post_save, sender=Order)
def notify_user_when_order_created(sender, **kwargs):
    try:
        order = kwargs['instance']
        is_new = kwargs['created']
        if is_new:
            notify_user_when_order_status_created_or_changed(order, order.status)
    except Exception, e:
        logger.error('notify user when order created: {0}', e.message)


class QueryOrderRequestHandler(object):
    #订单查询
    COMMAND_KEY_ORDER_QUERY = "ddcx"

    @staticmethod
    def get_unbind_message():
        redirect_uri = "http://{site_name}{bind_api}".format(site_name=settings.SITE_NAME,
                                                             bind_api=reverse('wechat:bind'))
        # 测试帐号只支持AUTH_CODE_TYPE_BASE，正式版本修改为AUTH_CODE_TYPE_USER_INFO
        scope_type = WeChatUserAuth.AUTH_CODE_TYPE_USER_INFO
        if settings.DEBUG:
            scope_type = WeChatUserAuth.AUTH_CODE_TYPE_BASE
        bind_url = WeChatUserAuth.get_auth_code_api(redirect_uri=redirect_uri,
                                                    params=None,
                                                    app_id=settings.WECHAT_APPID,
                                                    scope_type=scope_type)
        return u"微信号未和帐号绑定. 打开下面链接进行绑定\n<a href='{bind_url}'>绑定帐号</a>".format(bind_url=bind_url)

    def can_handle(self, request):
        if isinstance(request, WeChatTextRequest):
            return request.content.strip().lower().startswith(QueryOrderRequestHandler.COMMAND_KEY_ORDER_QUERY)
        elif isinstance(request, WeChatEventRequest):
            return request.event_type == request.type_menu_click and request.event_key == WeChatMenu.key_order_query
        return False

    def usage(self):
        return u'{cmd}+订单号:查询指定的订单详细信息'.format(cmd=QueryOrderRequestHandler.COMMAND_KEY_ORDER_QUERY)

    def get_response(self, request):
        def get_order_id(input_cmd):
            input_cmd = input_cmd.strip()
            return input_cmd[len(QueryOrderRequestHandler.COMMAND_KEY_ORDER_QUERY):].strip()

        def query_all_processing_orders(my_order):
            """
            查询所有处理中的订单
            """
            not_paid_orders = my_order.get_by_status(Order.ORDER_STATUS_DRAFT)
            paid_orders = my_order.get_by_status(Order.ORDER_STATUS_PAID)
            shipped_orders = my_order.get_by_status(Order.ORDER_STATUS_SHIPPED)

            processing_orders = not_paid_orders + paid_orders + shipped_orders
            processing_order_count = len(processing_orders)
            if 0 == processing_order_count:
                handled_result = u'您暂无在途订单'
            elif 1 == processing_order_count:
                #TODO: 商品有多个这个需要修改
                order_summary = processing_orders[0]
                product_names = []
                for index, product_name in enumerate(order_summary.products.values()):
                    product_names.append(u'{index}. {product_name}'.format(index=index, product_name=product_name))
                handled_result = u'您的订单（" {order_id} ）" {order_status} \n订单商品列表:\n{product_names}'.format(
                    order_id=order_summary.id,
                    order_status=order_summary.status_text,
                    product_names='\n'.join(product_names)
                )
            else:
                order_ids = []
                for index, order_summary in enumerate(processing_orders):
                    order_ids.append(u"{index}. {order_id} {oder_status}".format(index=index,
                                                                                 order_id=order_summary.id,
                                                                                 oder_status=order_summary.status_text))
                tip_message = u'你可以输入："{cmd}"+订单号来查询指定的订单详细信息'.format(
                    cmd=QueryOrderRequestHandler.COMMAND_KEY_ORDER_QUERY)
                handled_result = u'您的所有在途订单：\n{order_ids}\n\n{tip_message}'.format(
                    order_ids="\n".join(order_ids),
                    tip_message=tip_message
                )
            return handled_result

        def query_order(my_order, order_id):
            """
            查询指定订单详细情况
            """
            order_summary = None
            for cur_order_summary in my_order:
                if order_id == cur_order_summary.id:
                    order_summary = cur_order_summary
                    break
            if not order_summary:
                handled_result = u'您输入的订单（{order_id}）不存在，请核对订单后再试'.format(order_id=order_id)
            else:
                product_names = []
                for index, product_name in enumerate(order_summary.products.values()):
                    product_names.append(u'{index}. {product_name}'.format(index=index, product_name=product_name))
                handled_result = u'您的订单（{order_id}） {order_status} \n订单商品列表:\n{product_names}'.format(
                    order_id=order_summary.id,
                    order_status=order_summary.status_text,
                    product_names='\n'.join(product_names)
                )
            return handled_result

        wechat_user = WeChatUser.objects.get_bound_user(request.from_user_name)
        if wechat_user:
            user = wechat_user.customer
            my_order = MyOrders(user=user)
            if isinstance(request, WeChatTextRequest):
                query_order_id = get_order_id(request.content)
                message_content = query_order(my_order=my_order, order_id=query_order_id)
            else:
                message_content = query_all_processing_orders(my_order=my_order)
        else:
            message_content = QueryOrderRequestHandler.get_unbind_message()
        return WeChatTextResponse(request, message_content)


class CancelOrderRequestHandler(object):
    #订单取消
    COMMAND_KEY_ORDER_CANCEL = "ddqx"

    def can_handle(self, request):
        if isinstance(request, WeChatTextRequest):
            return request.content.strip().lower().startswith(CancelOrderRequestHandler.COMMAND_KEY_ORDER_CANCEL)
        elif isinstance(request, WeChatEventRequest):
            return request.event_type == request.type_menu_click and request.event_key == WeChatMenu.key_cancel_query
        return False

    def usage(self):
        return u'{cmd}+订单号：取消您的订单'.format(cmd=CancelOrderRequestHandler.COMMAND_KEY_ORDER_CANCEL)

    def get_response(self, request):
        def get_order_id(input_cmd):
            input_cmd = input_cmd.strip()
            return input_cmd[len(CancelOrderRequestHandler.COMMAND_KEY_ORDER_CANCEL):].strip()

        def cancel_order(user, order_id):
            """
            取消订单
            """
            handled_result = u'订单（{oder_id}）不存在，请核对订单后再试'.format(order_id=order_id)
            if order_id:
                order_list = Order.objects.filter(owner=user, id=order_id)
                if order_list:
                    order = order_list[0]
                    if Order.ORDER_STATUS_DRAFT != order.status:
                        handled_result = u'订单（{oder_id}） {order_status}，无法取消'.format(
                            order_id=order_id,
                            order_status=order.status
                        )
                    else:
                        #TODO: 订单取消函数，actor 是否正确需要确定
                        if order.set_status(new_status=Order.ORDER_STATUS_CANCEL, actor=user):
                            handled_result = u'订单（{oder_id}），已经成功取消'.format(order_id=order_id)
                        else:
                            handled_result = u'订单（{oder_id}） {order_status}，取消订单失败'.format(
                                order_id=order_id,
                                order_status=order.status
                            )
            return handled_result

        def candidate_cancel_orders(user):
            my_order = MyOrders(user=user)
            not_paid_orders = my_order.get_by_status(Order.ORDER_STATUS_DRAFT)
            candidate_orders = not_paid_orders
            candidate_order_count = len(candidate_orders)
            if 0 == candidate_order_count:
                handled_result = u'您暂无可以取消的订单'
            else:
                order_ids = []
                for index, order_summary in enumerate(candidate_orders):
                    order_ids.append(u"{index}. {order_id} {oder_status}".format(index=index,
                                                                                 order_id=order_summary.id,
                                                                                 oder_status=order_summary.status_text))
                tip_message = u'你可以输入："{cmd}"+订单号来取消指定的订单'.format(
                    cmd=CancelOrderRequestHandler.COMMAND_KEY_ORDER_CANCEL)
                handled_result = u'您可以取消的订单：\n{order_ids}\n\n{tip_message}'.format(
                    order_ids="\n".join(order_ids),
                    tip_message=tip_message
                )
            return handled_result

        wechat_user = WeChatUser.objects.get_bound_user(request.from_user_name)
        if wechat_user:
            user = wechat_user.customer
            if isinstance(request, WeChatTextRequest):
                cancel_order_id = get_order_id(request.content)
                message_content = cancel_order(user=user, order_id=cancel_order_id)
            else:
                message_content = candidate_cancel_orders(user)
        else:
            message_content = QueryOrderRequestHandler.get_unbind_message()
        return WeChatTextResponse(request, message_content)
