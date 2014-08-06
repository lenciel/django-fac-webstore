#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import hashlib

from django.http import HttpResponseForbidden
from django.test import TestCase
from django.test.client import Client
from django.test.utils import setup_test_environment
from django.conf import settings

setup_test_environment()

logger = logging.getLogger(u"test")


class BaseTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def post_data(self, url, content_type, data, **extra):
        return self.client.post(url, content_type=content_type, data=data, **extra)

    def get_data(self, url):
        return self.client.get(url)


class WeChatVerifyTest(BaseTestCase):
    @staticmethod
    def generate_signature(nonce, timestamp, token):
        s = [token, timestamp, nonce]
        s.sort()
        s = ''.join(s)
        return hashlib.sha1(s).hexdigest()

    def test_verify_get(self):
        nonce = 'abcd'
        timestamp = '2014'
        token = settings.WECHAT_TOKEN
        signature = WeChatVerifyTest.generate_signature(nonce, timestamp, token)
        echostr = 'fine'
        url = '/wechat/api?signature={0}&timestamp={1}&nonce={2}&echostr={3}' \
            .format(signature, timestamp, nonce, echostr)
        resp = self.get_data(url)
        self.assertEqual(echostr, resp.content)

    def test_verify_get_fail(self):
        nonce = 'abcd'
        timestamp = '2014'
        signature = 'bad'
        echostr = 'fine'
        url = '/wechat/api?signature={0}&timestamp={1}&nonce={2}&echostr={3}'.format(signature, timestamp, nonce, echostr)
        resp = self.get_data(url)
        self.assertNotEqual(echostr, resp.content)

    def test_verify_post(self):
        nonce = 'abcd'
        timestamp = '2014'
        token = settings.WECHAT_TOKEN
        signature = WeChatVerifyTest.generate_signature(nonce, timestamp, token)
        echostr = 'fine'
        data = """<xml>
            <ToUserName><![CDATA[toUser]]></ToUserName>
            <FromUserName><![CDATA[fromUser]]></FromUserName>
            <CreateTime>1348831860</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[What is WIFI password ?]]></Content>
            <MsgId>1234567890123456</MsgId>
            </xml>
        """
        url = '/wechat/api?signature={0}&timestamp={1}&nonce={2}&echostr={3}' \
            .format(signature, timestamp, nonce, echostr)
        resp = self.post_data(url, "application/xml", data)
        self.assertIsNotNone(resp.content, "response should not none")
        self.assertNotEqual('', resp.content)

    def test_verify_invalid_post(self):
        nonce = 'abcd'
        timestamp = '2014'
        signature = 'invalid'
        echostr = 'fine'
        data = """<xml>
            <ToUserName><![CDATA[toUser]]></ToUserName>
            <FromUserName><![CDATA[fromUser]]></FromUserName>
            <CreateTime>1348831860</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[What is WIFI password ?]]></Content>
            <MsgId>1234567890123456</MsgId>
            </xml>
        """
        url = '/wechat/api?signature={0}&timestamp={1}&nonce={2}&echostr={3}' \
            .format(signature, timestamp, nonce, echostr)
        resp = self.post_data(url, "application/xml", data)
        self.assertIsInstance(resp, HttpResponseForbidden)

