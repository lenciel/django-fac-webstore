#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from django.test import TestCase
from django.test.utils import setup_test_environment
from apps.product.models import Product
from apps.wechat.handlers import UsageRequestHandler, RequestDispatcher, \
    UnknownTextRequestHandler, QueryOrderRequestHandler, CancelOrderRequestHandler, \
    ProductSearchRequestHandler, SubscribeEventHandler, ProductSearchEventHandler
from apps.wechat.menu import WeChatMenu
from apps.wechat.models import WeChatUser
from apps.wechat.protocols import WeChatTextRequest, WeChatEventRequest, WeChatNewsResponse, WeChatTextResponse


setup_test_environment()

logger = logging.getLogger(u"test")


class TestRequestDispatcher(TestCase):
    def test_resolve_text_xml_to_request(self):
        text_xml = """
        <xml>
        <ToUserName><![CDATA[toUser]]></ToUserName>
        <FromUserName><![CDATA[fromUser]]></FromUserName>
        <CreateTime>1348831860</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[this is a test]]></Content>
        <MsgId>1234567890123456</MsgId>
        </xml>
        """
        dispatcher = RequestDispatcher()
        self.assertEqual(True, isinstance(dispatcher.resolve_xml_to_request(text_xml), WeChatTextRequest))

    def test_resolve_event_xml_to_request(self):
        event_xml = """
        <xml>
        <ToUserName><![CDATA[toUser]]></ToUserName>
        <FromUserName><![CDATA[FromUser]]></FromUserName>
        <CreateTime>123456789</CreateTime>
        <MsgType><![CDATA[event]]></MsgType>
        <Event><![CDATA[subscribe]]></Event>
        </xml>
        """
        dispatcher = RequestDispatcher()
        self.assertEqual(True, isinstance(dispatcher.resolve_xml_to_request(event_xml), WeChatEventRequest))

    def test_dispatch_usage_request(self):
        request = WeChatTextRequest()
        r = RequestDispatcher()

        request.content = '?'
        self.assertEqual(True, isinstance(r.get_handler(request), UsageRequestHandler))

        request.content = u'？'
        self.assertEqual(True, isinstance(r.get_handler(request), UsageRequestHandler))

    def test_dispatch_query_order_request(self):
        request = WeChatTextRequest()
        r = RequestDispatcher()

        request.content = 'ddcx?'
        self.assertEqual(True, isinstance(r.get_handler(request), QueryOrderRequestHandler))

    def test_dispatch_cancel_order_request(self):
        request = WeChatTextRequest()
        r = RequestDispatcher()

        request.content = 'ddqx?'
        self.assertEqual(True, isinstance(r.get_handler(request), CancelOrderRequestHandler))

    def test_dispatch_search_request(self):
        request = WeChatTextRequest()
        r = RequestDispatcher()

        request.content = 'spss?'
        self.assertEqual(True, isinstance(r.get_handler(request), ProductSearchRequestHandler))

    def test_dispatch_unknown_request(self):
        request = WeChatTextRequest()
        r = RequestDispatcher()

        request.content = 'hello'
        self.assertEqual(True, isinstance(r.get_handler(request), UnknownTextRequestHandler))

    def test_dispatch_subscribe_event_request(self):
        request = WeChatEventRequest()
        r = RequestDispatcher()

        request.event_type = WeChatEventRequest.type_subscribe
        request.is_subscribe = True
        self.assertEqual(True, isinstance(r.get_handler(request), SubscribeEventHandler))

        request.is_subscribe = False
        self.assertEqual(True, isinstance(r.get_handler(request), SubscribeEventHandler))

    def test_dispatch_order_query_event_request(self):
        request = WeChatEventRequest()
        r = RequestDispatcher()

        request.event_type = WeChatEventRequest.type_menu_click
        request.event_key = WeChatMenu.key_order_query
        self.assertEqual(True, isinstance(r.get_handler(request), QueryOrderRequestHandler))

    def test_dispatch_order_cancel_event_request(self):
        request = WeChatEventRequest()
        r = RequestDispatcher()

        request.event_type = WeChatEventRequest.type_menu_click
        request.event_key = WeChatMenu.key_cancel_query
        self.assertEqual(True, isinstance(r.get_handler(request), CancelOrderRequestHandler))

    def test_dispatch_none_event_request(self):
        request = WeChatEventRequest()
        r = RequestDispatcher()

        exception_occurred = False
        try:
            request.event_type = WeChatEventRequest.type_none
            r.get_handler(request)
        except Exception:
            exception_occurred = True

        self.assertTrue(exception_occurred)


class TestTextUsageHandler(TestCase):
    def test_usage(self):
        request = WeChatTextRequest()
        request.content = '?'
        handler = UsageRequestHandler()
        response = handler.get_response(request)
        self.assertEqual(RequestDispatcher.usage(), response.content)


class TestUnknownTextRequestHandler(TestCase):
    def test_response(self):
        request = WeChatTextRequest()
        request.content = ' '
        handler = UnknownTextRequestHandler()
        response = handler.get_response(request)
        self.assertEqual(UnknownTextRequestHandler.unknown_command, response.content)


class TestProductSearchRequestHandler(TestCase):

    @staticmethod
    def gen_scan_request():
        request_content = '''<xml>
            <ToUserName><![CDATA[toUser]]></ToUserName>
            <FromUserName><![CDATA[fromUser]]></FromUserName>
            <CreateTime>159753</CreateTime>
            <MsgType><![CDATA[event]]></MsgType>
            <Event><![CDATA[{0}]]></Event>
            <EventKey><![CDATA[{1}]]></EventKey>
            </xml>'''.format(WeChatEventRequest.event_value_click, WeChatMenu.key_scan)
        return request_content

    def test_normal(self):
        product1 = "product1"
        product2 = "product2"
        product3 = "product3"
        Product.objects.create(name=product1, creator_id=1, provider_id=1, category_id=1, is_published=True)
        Product.objects.create(name=product2, creator_id=1, provider_id=1, category_id=1, is_published=True)
        Product.objects.create(name=product3, creator_id=1, provider_id=1, category_id=1, is_published=True)

        response = RequestDispatcher.process(self.gen_scan_request())

        self.assertTrue(isinstance(response, WeChatNewsResponse))
        self.assertEqual(3, len(response.article_list))
        # order_by '-update' so the last one should be displayed as first
        self.assertEqual(product3, response.article_list[0][WeChatNewsResponse.tag_title])
        self.assertEqual(product2, response.article_list[1][WeChatNewsResponse.tag_title])
        self.assertEqual(product1, response.article_list[2][WeChatNewsResponse.tag_title])

    def test_empty(self):
        response = RequestDispatcher.process(self.gen_scan_request())

        self.assertTrue(isinstance(response, WeChatTextResponse))
        self.assertEqual(u'暂无商品', response.content)

    def test_more_than_10(self):
        product4 = "product4"
        product12 = "product12"
        Product.objects.create(name='product1', creator_id=1, provider_id=1, category_id=1, is_published=True)
        Product.objects.create(name='product2', creator_id=1, provider_id=1, category_id=1, is_published=True)
        Product.objects.create(name='product3', creator_id=1, provider_id=1, category_id=1, is_published=True)
        Product.objects.create(name=product4, creator_id=1, provider_id=1, category_id=1, is_published=True)
        Product.objects.create(name='product5', creator_id=1, provider_id=1, category_id=1, is_published=True)
        Product.objects.create(name='product6', creator_id=1, provider_id=1, category_id=1, is_published=True)
        Product.objects.create(name='product7', creator_id=1, provider_id=1, category_id=1, is_published=True)
        Product.objects.create(name='product8', creator_id=1, provider_id=1, category_id=1, is_published=True)
        Product.objects.create(name='product9', creator_id=1, provider_id=1, category_id=1, is_published=True)
        Product.objects.create(name='product10', creator_id=1, provider_id=1, category_id=1, is_published=True)
        Product.objects.create(name='product11', creator_id=1, provider_id=1, category_id=1, is_published=True)
        Product.objects.create(name=product12, creator_id=1, provider_id=1, category_id=1, is_published=True)

        response = RequestDispatcher.process(self.gen_scan_request())

        self.assertTrue(isinstance(response, WeChatNewsResponse))
        self.assertEqual(10, len(response.article_list))
        # order_by '-update' so the last one should be displayed as first
        self.assertEqual(product12, response.article_list[0][WeChatNewsResponse.tag_title])
        self.assertEqual(product4, response.article_list[8][WeChatNewsResponse.tag_title])
        self.assertEqual(u'更多商品', response.article_list[9][WeChatNewsResponse.tag_title])
        self.assertEqual(u'点击查看更多商品', response.article_list[9][WeChatNewsResponse.tag_description])


class TestProductSearchEventHandler(TestCase):
    user_name = 'foo'

    @staticmethod
    def gen_search_event_request():
        request_content = '''<xml>
            <ToUserName><![CDATA[toUser]]></ToUserName>
            <FromUserName><![CDATA[{0}]]></FromUserName>
            <CreateTime>159753</CreateTime>
            <MsgType><![CDATA[event]]></MsgType>
            <Event><![CDATA[{1}]]></Event>
            <EventKey><![CDATA[{2}]]></EventKey>
            </xml>'''.format(TestProductSearchEventHandler.user_name,
                             WeChatEventRequest.event_value_click,
                             WeChatMenu.key_search)
        WeChatUser.objects.create(openid=TestProductSearchEventHandler.user_name)
        return request_content

    @staticmethod
    def gen_search_text_request(content):
        request_content = '''<xml>
            <ToUserName><![CDATA[toUser]]></ToUserName>
            <FromUserName><![CDATA[{0}]]></FromUserName>
            <CreateTime>159753</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[{1}]]></Content>
            <MsgId>1234567890123456</MsgId>
            </xml>'''.format(TestProductSearchEventHandler.user_name, content)
        return request_content

    def test_normal(self):
        keyword1 = 'product'
        keyword2 = 'p'
        product1 = "product1"
        product2 = "product2"
        product3 = "p3"
        Product.objects.create(name=product1, creator_id=1, provider_id=1, category_id=1, is_published=True)
        Product.objects.create(name=product2, creator_id=1, provider_id=1, category_id=1, is_published=True)
        Product.objects.create(name=product3, creator_id=1, provider_id=1, category_id=1, is_published=True)

        response = RequestDispatcher.process(self.gen_search_event_request())

        self.assertTrue(isinstance(response, WeChatTextResponse))
        self.assertEqual(u'请直接回复商品关键字来搜索您想要的商品。以后您也可以随时通过发送快捷命令spss+关键字来直接搜索。',
                         response.content)
        self.assertTrue(ProductSearchEventHandler.is_search_activated(TestProductSearchEventHandler.user_name))

        response = RequestDispatcher.process(self.gen_search_text_request(keyword1))
        self.assertTrue(isinstance(response, WeChatNewsResponse))
        self.assertEqual(2, len(response.article_list))
        # order_by '-update' so the last one should be displayed as first
        self.assertEqual(product2, response.article_list[0][WeChatNewsResponse.tag_title])
        self.assertEqual(product1, response.article_list[1][WeChatNewsResponse.tag_title])

        response = RequestDispatcher.process(self.gen_search_text_request(keyword2))
        self.assertTrue(isinstance(response, WeChatNewsResponse))
        self.assertEqual(3, len(response.article_list))
        # order_by '-update' so the last one should be displayed as first
        self.assertEqual(product3, response.article_list[0][WeChatNewsResponse.tag_title])
        self.assertEqual(product2, response.article_list[1][WeChatNewsResponse.tag_title])
        self.assertEqual(product1, response.article_list[2][WeChatNewsResponse.tag_title])

    def test_other_command_interrupted(self):
        keyword1 = 'product'
        product1 = "product1"
        product2 = "product2"
        product3 = "p3"
        Product.objects.create(name=product1, creator_id=1, provider_id=1, category_id=1, is_published=True)
        Product.objects.create(name=product2, creator_id=1, provider_id=1, category_id=1, is_published=True)
        Product.objects.create(name=product3, creator_id=1, provider_id=1, category_id=1, is_published=True)

        response = RequestDispatcher.process(self.gen_search_event_request())

        self.assertTrue(isinstance(response, WeChatTextResponse))
        self.assertEqual(u'请直接回复商品关键字来搜索您想要的商品。以后您也可以随时通过发送快捷命令spss+关键字来直接搜索。',
                         response.content)
        self.assertTrue(ProductSearchEventHandler.is_search_activated(TestProductSearchEventHandler.user_name))

        # send a help text request which will be handled normally
        response = RequestDispatcher.process(self.gen_search_text_request('?'))
        self.assertTrue(ProductSearchEventHandler.is_search_activated(TestProductSearchEventHandler.user_name))
        self.assertFalse(isinstance(response, WeChatNewsResponse))

        # send an unknown text request which will be regarded as query keyword
        response = RequestDispatcher.process(self.gen_search_text_request(keyword1))
        self.assertTrue(isinstance(response, WeChatNewsResponse))
        self.assertEqual(2, len(response.article_list))
        # order_by '-update' so the last one should be displayed as first
        self.assertEqual(product2, response.article_list[0][WeChatNewsResponse.tag_title])
        self.assertEqual(product1, response.article_list[1][WeChatNewsResponse.tag_title])
