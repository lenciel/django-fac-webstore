#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import OrderedDict

import json
import logging
import os

logger = logging.getLogger('apps.'+os.path.basename(os.path.dirname(__file__)))


class WeChatMenu:
    # static values to build menu and be used on handling menu click event.
    key_scan = 'key_scan'
    key_search = 'key_search'
    key_order_query = 'query_order'
    key_cancel_query = 'cancel_order'

    @staticmethod
    def build_as_json():
        buttons = {
            'button': [
                WeChatMenu._gen_sub_button(u'商品信息', [
                    WeChatMenu._gen_click_button(u'浏览商品', WeChatMenu.key_scan),
                    WeChatMenu._gen_click_button(u'搜索商品', WeChatMenu.key_search)
                ]),
                WeChatMenu._gen_sub_button(u'我的', [
                    WeChatMenu._gen_click_button(u'查询订单', WeChatMenu.key_order_query),
                    WeChatMenu._gen_click_button(u'取消订单', WeChatMenu.key_cancel_query)
                ])
            ]
        }
        return json.dumps(obj=buttons,
                          ensure_ascii=False,
                          indent=4,
                          separators=(',', ':'))

    @staticmethod
    def _gen_sub_button(name, buttons):
        sub_button = OrderedDict()
        sub_button['name'] = name
        sub_button['sub_button'] = buttons
        return sub_button

    @staticmethod
    def _gen_click_button(name, key):
        button = OrderedDict()
        button['type'] = 'click'
        button['name'] = name
        button['key'] = key
        return button

    @staticmethod
    def _gen_view_button(name, url):
        button = OrderedDict()
        button['type'] = 'view'
        button['name'] = name
        button['url'] = url
        return button
