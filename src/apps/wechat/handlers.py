#!/usr/bin/env python
# -*- coding: utf-8 -*-
from urlparse import urljoin
from xml.dom import minidom
import time
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.db.models import Q

from apps.product.models import Product
from apps.wechat.menu import WeChatMenu
from apps.wechat.models import WeChatUser, logger
from apps.wechat.order import QueryOrderRequestHandler, CancelOrderRequestHandler
from apps.wechat.protocols import WeChatEventRequest, WeChatTextRequest, WeChatRequest
from apps.wechat.protocols import WeChatTextResponse, WeChatNewsResponse


class RequestHandler(object):
    def get_response(self, request):
        raise NotImplementedError


class TextRequestHandler(RequestHandler):
    def can_handle(self, request):
        raise NotImplementedError

    def usage(self):
        return NotImplementedError


class UsageRequestHandler(TextRequestHandler):
    question_marks = {'?', u'？'}

    def can_handle(self, request):
        if isinstance(request, WeChatTextRequest):
            return request.content in UsageRequestHandler.question_marks
        return False

    def get_response(self, request):
        return WeChatTextResponse(request, RequestDispatcher.usage())

    def usage(self):
        # 该函数表示将要添加到usage字符串中的文字，返回空
        return ''


class ProductSearchRequestHandler(TextRequestHandler):
    search_prefix = 'spss'
    max_display_count = 10

    def can_handle(self, request):
        if isinstance(request, WeChatTextRequest):
            return request.content.startswith(self.search_prefix)
        elif isinstance(request, WeChatEventRequest):
            return request.event_type == request.type_menu_click and request.event_key == WeChatMenu.key_scan
        return False

    def usage(self):
        return u'spss+搜索关键字：快捷搜索符合关键字的商品\n或者点击菜单里\'浏览商品\'选项来查看所有商品'

    def get_response(self, request):
        if isinstance(request, WeChatTextRequest):
            keyword = request.content[len(self.search_prefix):]
            return self.query_products(request, keyword)
        elif isinstance(request, WeChatEventRequest):
            return self.query_products(request)
        return None

    def query_products(self, request, keyword=None):
        query_set = Product.active_objects.order_by('-rating', '-updated').filter(is_published=True)

        if keyword is not None:
            query_set = query_set.filter(Q(name__contains=keyword) | Q(summary__contains=keyword))

        count = query_set.count()
        if count == 0:
            if keyword is None:
                content = u'暂无商品'
            else:
                content = u'未找到指定商品'
            return WeChatTextResponse(request=request, content=content)

        if count > self.max_display_count:
            # if result size is larger than max_display_count
            # we should only get the (max_display_count - 1) products
            # and put a special item which represents all rest items of the result at the end
            products = query_set.all()[:self.max_display_count - 1]
        else:
            products = query_set.all()

        response = WeChatNewsResponse(request=request)
        for product in products:
            pic_url = product.title_image_url()
            if pic_url:
                pic_url = urljoin('http://' + settings.SITE_NAME, pic_url)

            product_url = urljoin('http://' + settings.SITE_NAME,
                                  reverse('wechat:product_detail', args=[str(product.id)]))
            response.add_article(title=product.name,
                                 desc=product.summary,
                                 pic_url=pic_url,
                                 url=product_url)

        if count > self.max_display_count:
            # put the special item
            #TODO: add a default image?
            response.add_article(title=u'更多商品',
                                 desc=u'点击查看更多商品',
                                 pic_url='',
                                 #TODO: use reverse('wechat:product_list') instead later
                                 url='mock_url')
        return response


class UnknownTextRequestHandler(TextRequestHandler):
    unknown_command = u'亲，小应暂时不能理解您说的。不过您可以试试回复"?"来获取小应明白的命令。'

    def can_handle(self, request):
        # 肯定能处理所有消息
        return True

    def usage(self):
        return ''

    def get_response(self, request):
        if ProductSearchEventHandler.is_search_activated(request.from_user_name):
            return ProductSearchRequestHandler().query_products(request=request, keyword=request.content)
        return WeChatTextResponse(request=request, content=UnknownTextRequestHandler.unknown_command)


class ProductSearchEventHandler(TextRequestHandler):
    # once product search starts, user will have 60 seconds to input the keyword to search.
    # after that any unknown text request will be regarded as unknown command
    search_duration_in_secs = 60

    def can_handle(self, request):
        if isinstance(request, WeChatEventRequest):
            return request.event_type == request.type_menu_click and request.event_key == WeChatMenu.key_search
        return False

    def get_response(self, request):
        self._set_start_search_time(request.from_user_name, int(time.time()))
        return WeChatTextResponse(request,
                                  u'请直接回复商品关键字来搜索您想要的商品。以后您也可以随时通过发送快捷命令spss+关键字来直接搜索。')

    @staticmethod
    def _set_start_search_time(user_name, value):
        try:
            bind_user = WeChatUser.objects.get(openid=user_name)
            bind_user.start_search_at = value
            bind_user.save()
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            logger.debug(u"未找到指定账号")

    @staticmethod
    def is_search_activated(user_name):
        try:
            bind_user = WeChatUser.objects.get(openid=user_name)
            return int(time.time()) - bind_user.start_search_at <= ProductSearchEventHandler.search_duration_in_secs
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return False


class SubscribeEventHandler(RequestHandler):
    welcome_msg_subscribe = u'您好！我是小应，很高兴为您服务。回复"?"了解更多使用方法'

    def can_handle(self, request):
        return request.event_type == request.type_subscribe

    def get_response(self, request):
        response = None
        wechat_user = WeChatUser.objects.filter(openid=request.from_user_name)
        if request.is_subscribe:
            response = WeChatTextResponse(request, SubscribeEventHandler.welcome_msg_subscribe)
            if not wechat_user:
                WeChatUser.objects.create(openid=request.from_user_name)
        else:
            if wechat_user:
                wechat_user.delete()
        return response


class RequestDispatcher(object):
    text_handlers = [
        UsageRequestHandler(), QueryOrderRequestHandler(), CancelOrderRequestHandler(),
        ProductSearchRequestHandler(), UnknownTextRequestHandler()]

    event_handlers = [SubscribeEventHandler(), ProductSearchRequestHandler(), ProductSearchEventHandler(),
                      QueryOrderRequestHandler(), CancelOrderRequestHandler()]

    text_request_usage = ''

    @staticmethod
    def process(request_content):
        r = RequestDispatcher()
        request = r.resolve_xml_to_request(request_content)
        handler = r.get_handler(request)
        return handler.get_response(request)

    def resolve_xml_to_request(self, xml):
        doc = minidom.parseString(xml)
        root = doc.documentElement
        msg_type = doc.getElementsByTagName(WeChatRequest.tag_msg_type)[0].firstChild.data

        if msg_type == 'text':
            return WeChatTextRequest().parse(root)
        elif msg_type == 'event':
            return WeChatEventRequest().parse(root)
        else:
            return None

    def get_handler(self, request):
        if isinstance(request, WeChatTextRequest):
            return self.get_text_handler(request)
        elif isinstance(request, WeChatEventRequest):
            return self.get_event_handler(request)
        else:
            return None

    def get_text_handler(self, request):
        for handler in RequestDispatcher.text_handlers:
            if handler.can_handle(request):
                return handler

        # supposed not get here.
        raise Exception

    def get_event_handler(self, request):
        for handler in RequestDispatcher.event_handlers:
            if handler.can_handle(request):
                return handler

        # supposed not get here.
        raise Exception

    @staticmethod
    def usage():
        if not RequestDispatcher.text_request_usage:
            t = u'您可以直接使用底部菜单选择相应功能。或者尝试以下命令：'
            for handler in RequestDispatcher.text_handlers:
                if handler.usage():
                    t += '\n' + handler.usage()
            RequestDispatcher.text_request_usage = t

        return RequestDispatcher.text_request_usage
