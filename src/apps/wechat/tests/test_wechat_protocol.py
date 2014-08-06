#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from xml.dom import minidom

from django.test import TestCase
from django.test.utils import setup_test_environment
from apps.wechat.protocols import WeChatTextResponse, WeChatNewsResponse, WeChatTextRequest, WeChatEventRequest,\
    WeChatImageResponse

setup_test_environment()

logger = logging.getLogger(u"test")


class WeChatRequestTest(TestCase):
    def test_text_request(self):
        to_user = 'toUser'
        from_user = 'fromUser'
        time = 159753
        msg_type = 'text'
        msg_content = 'Hello world.'
        msg_id = 951357
        request_content = '''<xml>
            <ToUserName><![CDATA[{0}]]></ToUserName>
            <FromUserName><![CDATA[{1}]]></FromUserName>
            <CreateTime>{2}</CreateTime>
            <MsgType><![CDATA[{3}]]></MsgType>
            <Content><![CDATA[{4}]]></Content>
            <MsgId>{5}</MsgId>
            </xml>'''.format(to_user, from_user, time, msg_type, msg_content, msg_id)
        request = WeChatTextRequest().parse(request_content)

        self.assertTrue(isinstance(request, WeChatTextRequest))
        self.assertEqual(to_user, request.to_user_name)
        self.assertEqual(from_user, request.from_user_name)
        self.assertEqual(time, request.create_time)
        self.assertEqual(msg_content, request.content)
        self.assertEqual(msg_id, request.msg_id)

    def test_subscribe_request(self):
        to_user = 'toUser'
        from_user = 'fromUser'
        time = 159753
        msg_type = 'event'
        event_value = 'unsubscribe'
        request_content = '''<xml>
            <ToUserName><![CDATA[{0}]]></ToUserName>
            <FromUserName><![CDATA[{1}]]></FromUserName>
            <CreateTime>{2}</CreateTime>
            <MsgType><![CDATA[{3}]]></MsgType>
            <Event><![CDATA[{4}]]></Event>
            </xml>'''.format(to_user, from_user, time, msg_type, event_value)
        request = WeChatEventRequest().parse(request_content)

        self.assertTrue(isinstance(request, WeChatEventRequest))
        self.assertEqual(to_user, request.to_user_name)
        self.assertEqual(from_user, request.from_user_name)
        self.assertEqual(time, request.create_time)
        self.assertEqual(WeChatEventRequest.type_subscribe, request.event_type)
        self.assertFalse(request.is_subscribe)

    def test_menu_click_request(self):
        to_user = 'toUser'
        from_user = 'fromUser'
        time = 159753
        msg_type = 'event'
        event_value = 'CLICK'
        event_key = 'key123'
        request_content = '''<xml>
            <ToUserName><![CDATA[{0}]]></ToUserName>
            <FromUserName><![CDATA[{1}]]></FromUserName>
            <CreateTime>{2}</CreateTime>
            <MsgType><![CDATA[{3}]]></MsgType>
            <Event><![CDATA[{4}]]></Event>
            <EventKey><![CDATA[{5}]]></EventKey>
            </xml>'''.format(to_user, from_user, time, msg_type, event_value, event_key)
        request = WeChatEventRequest().parse(request_content)

        self.assertTrue(isinstance(request, WeChatEventRequest))
        self.assertEqual(to_user, request.to_user_name)
        self.assertEqual(from_user, request.from_user_name)
        self.assertEqual(time, request.create_time)
        self.assertEqual(WeChatEventRequest.type_menu_click, request.event_type)
        self.assertEqual(event_key, request.event_key)


class WeChatResponseTest(TestCase):
    def test_text_response(self):
        to_user = 'toUser'
        from_user = 'fromUser'
        res_msg = 'response message'
        request_content = '''<xml>
            <ToUserName><![CDATA[{0}]]></ToUserName>
            <FromUserName><![CDATA[{1}]]></FromUserName>
            <CreateTime>159753</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[Hello world.]]></Content>
            <MsgId>951357</MsgId>
            </xml>'''.format(to_user, from_user)
        request = WeChatTextRequest().parse(request_content)
        response = WeChatTextResponse(request=request,
                                      content=res_msg)
        xml = response.to_xml()
        doc = minidom.parseString(xml)
        root = doc.documentElement
        expect_xml = '<xml>' \
                     '<ToUserName><![CDATA[{0}]]></ToUserName>' \
                     '<FromUserName><![CDATA[{1}]]></FromUserName>' \
                     '<CreateTime>{2}</CreateTime>' \
                     '<MsgType><![CDATA[text]]></MsgType>' \
                     '<Content><![CDATA[{3}]]></Content>' \
                     '</xml>'.format(from_user, to_user, root.getElementsByTagName('CreateTime')[0].firstChild.data,
                                     res_msg)
        self.assertEqual(expect_xml, xml)

    def test_image_response(self):
        to_user = 'toUser'
        from_user = 'fromUser'
        media_id = 'media_id123'
        request_content = '''<xml>
            <ToUserName><![CDATA[{0}]]></ToUserName>
            <FromUserName><![CDATA[{1}]]></FromUserName>
            <CreateTime>159753</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[Hello world.]]></Content>
            <MsgId>951357</MsgId>
            </xml>'''.format(to_user, from_user)
        request = WeChatTextRequest().parse(request_content)
        response = WeChatImageResponse(request=request,
                                       media_id=media_id)
        xml = response.to_xml()
        doc = minidom.parseString(xml)
        root = doc.documentElement
        expect_xml = '<xml>' \
                     '<ToUserName><![CDATA[{0}]]></ToUserName>' \
                     '<FromUserName><![CDATA[{1}]]></FromUserName>' \
                     '<CreateTime>{2}</CreateTime>' \
                     '<MsgType><![CDATA[image]]></MsgType>' \
                     '<Image>' \
                     '<MediaId><![CDATA[{3}]]></MediaId>'\
                     '</Image>' \
                     '</xml>'.format(from_user, to_user, root.getElementsByTagName('CreateTime')[0].firstChild.data,
                                     media_id)
        self.assertEqual(expect_xml, xml)

    def test_news_response(self):
        to_user = 'toUser'
        from_user = 'fromUser'
        title1 = 'title1'
        desc1 = 'desc1'
        pic_url1 = 'pic_url1'
        url1 = 'url1'
        title2 = 'title2'
        desc2 = 'desc2'
        pic_url2 = 'pic_url2'
        url2 = 'url2'
        request_content = '''<xml>
            <ToUserName><![CDATA[{0}]]></ToUserName>
            <FromUserName><![CDATA[{1}]]></FromUserName>
            <CreateTime>159753</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[Hello world.]]></Content>
            <MsgId>951357</MsgId>
            </xml>'''.format(to_user, from_user)
        request = WeChatTextRequest().parse(request_content)
        response = WeChatNewsResponse(request=request)
        response.add_article(title=title1,
                             desc=desc1,
                             pic_url=pic_url1,
                             url=url1)
        response.add_article(title=title2,
                             desc=desc2,
                             pic_url=pic_url2,
                             url=url2)
        xml = response.to_xml()
        doc = minidom.parseString(xml)
        root = doc.documentElement
        expect_xml = '<xml>' \
                     '<ToUserName><![CDATA[{0}]]></ToUserName>' \
                     '<FromUserName><![CDATA[{1}]]></FromUserName>' \
                     '<CreateTime>{2}</CreateTime>' \
                     '<MsgType><![CDATA[news]]></MsgType>' \
                     '<ArticleCount>{3}</ArticleCount>' \
                     '<Articles>' \
                     '<item>' \
                     '<Title><![CDATA[{4}]]></Title>' \
                     '<Description><![CDATA[{5}]]></Description>' \
                     '<PicUrl><![CDATA[{6}]]></PicUrl>' \
                     '<Url><![CDATA[{7}]]></Url>' \
                     '</item>' \
                     '<item>' \
                     '<Title><![CDATA[{8}]]></Title>' \
                     '<Description><![CDATA[{9}]]></Description>' \
                     '<PicUrl><![CDATA[{10}]]></PicUrl>' \
                     '<Url><![CDATA[{11}]]></Url>' \
                     '</item>' \
                     '</Articles>' \
                     '</xml>'.format(from_user, to_user, root.getElementsByTagName('CreateTime')[0].firstChild.data,
                                     '2',
                                     title1, desc1, pic_url1, url1,
                                     title2, desc2, pic_url2, url2,)

        self.assertEqual(expect_xml, xml)