#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import types
import time
from xml.dom import minidom

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


class WeChatBase(object):
    # common tags
    tag_create_time = 'CreateTime'
    tag_from_user_name = 'FromUserName'
    tag_to_user_name = 'ToUserName'
    tag_msg_type = 'MsgType'

    def __init__(self):
        # common data
        self.create_time = ''
        self.from_user_name = ''
        self.to_user_name = ''
        self.msg_type = ''


class WeChatRequest(WeChatBase):
    def __init__(self):
        super(WeChatRequest, self).__init__()

    def parse(self, dom):
        if isinstance(dom, types.StringTypes):
            root = minidom.parseString(dom).documentElement
        else:
            root = dom
        for param in root.childNodes:
            if param.childNodes:
                if param.tagName == self.tag_create_time:
                    self.create_time = int(param.childNodes[0].data)
                elif param.tagName == self.tag_from_user_name:
                    self.from_user_name = param.childNodes[0].data
                elif param.tagName == self.tag_to_user_name:
                    self.to_user_name = param.childNodes[0].data
                elif param.tagName == self.tag_msg_type:
                    self.msg_type = param.childNodes[0].data
                else:
                    self._handle_node(param)
            else:
                # FIXME:
                pass
        return self

    def _handle_node(self, node):
        pass


class WeChatTextRequest(WeChatRequest):
    # text tags
    tag_content = 'Content'
    tag_msg_id = 'MsgId'

    def __init__(self):
        super(WeChatTextRequest, self).__init__()
        self.content = ''
        self.msg_id = ''

    def _handle_node(self, node):
        if node.tagName == self.tag_content:
            self.content = node.childNodes[0].data.strip()
        elif node.tagName == self.tag_msg_id:
            self.msg_id = int(node.childNodes[0].data)


class WeChatEventRequest(WeChatRequest):
    # event tags
    tag_event = 'Event'
    tag_event_key = 'EventKey'
    # subscribe values
    event_value_subscribe = 'subscribe'
    event_value_unsubscribe = 'unsubscribe'
    # menu values
    event_value_click = 'CLICK'
    #types
    type_none = 0
    type_subscribe = 1
    type_menu_click = 2

    def __init__(self):
        super(WeChatEventRequest, self).__init__()
        self.is_subscribe = False
        self.event_type = self.type_none
        self.event_key = ''

    def _handle_node(self, node):
        if node.tagName == self.tag_event:
            value = node.childNodes[0].data
            if value == self.event_value_subscribe:
                self.is_subscribe = True
                self.event_type = self.type_subscribe
            elif value == self.event_value_unsubscribe:
                self.is_subscribe = False
                self.event_type = self.type_subscribe
            elif value == self.event_value_click:
                self.event_type = self.type_menu_click
                pass
        elif node.tagName == self.tag_event_key:
            self.event_key = node.childNodes[0].data


class WeChatResponse(WeChatBase):
    def __init__(self, request, msg_type):
        super(WeChatResponse, self).__init__()
        self.create_time = int(time.time())
        self.to_user_name = request.from_user_name
        self.from_user_name = request.to_user_name
        self.msg_type = msg_type

    def _to_xml_element(self, doc):
        xml = doc.createElement('xml')

        xml.appendChild(self._gen_cdata_node(doc, self.tag_to_user_name, self.to_user_name))
        xml.appendChild(self._gen_cdata_node(doc, self.tag_from_user_name, self.from_user_name))
        xml.appendChild(self._gen_text_node(doc, self.tag_create_time, self.create_time))
        xml.appendChild(self._gen_cdata_node(doc, self.tag_msg_type, self.msg_type))

        return xml

    def to_xml(self):
        doc = minidom.Document()
        return self._to_xml_element(doc).toxml(encoding='utf-8')

    @staticmethod
    def _gen_cdata_node(doc, tag, value):
        node = doc.createElement(tag)
        node.appendChild(doc.createCDATASection(value))
        return node

    @staticmethod
    def _gen_text_node(doc, tag, value):
        node = doc.createElement(tag)
        node.appendChild(doc.createTextNode(str(value)))
        return node


class WeChatTextResponse(WeChatResponse):
    # text tags
    tag_content = 'Content'

    def __init__(self, request, content=''):
        super(WeChatTextResponse, self).__init__(request, 'text')
        self.content = content

    def _to_xml_element(self, doc):
        xml = super(WeChatTextResponse, self)._to_xml_element(doc)
        xml.appendChild(self._gen_cdata_node(doc, self.tag_content, self.content))
        return xml


class WeChatImageResponse(WeChatResponse):
    # image tags
    tag_image = 'Image'
    tag_media_id = 'MediaId'

    def __init__(self, request, media_id):
        super(WeChatImageResponse, self).__init__(request, 'image')
        self.media_id = media_id

    def _to_xml_element(self, doc):
        xml = super(WeChatImageResponse, self)._to_xml_element(doc)
        image = doc.createElement(self.tag_image)
        image.appendChild(self._gen_cdata_node(doc, self.tag_media_id, self.media_id))
        xml.appendChild(image)
        return xml


class WeChatNewsResponse(WeChatResponse):
    # news tags
    tag_articles = 'Articles'
    tag_article_count = 'ArticleCount'
    tag_title = 'Title'
    tag_description = 'Description'
    tag_pic_url = 'PicUrl'
    tag_url = 'Url'
    tag_item = 'item'

    def __init__(self, request):
        super(WeChatNewsResponse, self).__init__(request, 'news')
        self.article_list = []

    def _to_xml_element(self, doc):
        xml = super(WeChatNewsResponse, self)._to_xml_element(doc)
        xml.appendChild(self._gen_text_node(doc, self.tag_article_count, len(self.article_list)))

        articles = doc.createElement(self.tag_articles)
        for article in self.article_list:
            item = doc.createElement(self.tag_item)

            item.appendChild(self._gen_cdata_node(doc, self.tag_title, article[self.tag_title]))
            item.appendChild(self._gen_cdata_node(doc, self.tag_description, article[self.tag_description]))
            item.appendChild(self._gen_cdata_node(doc, self.tag_pic_url, article[self.tag_pic_url]))
            item.appendChild(self._gen_cdata_node(doc, self.tag_url, article[self.tag_url]))

            articles.appendChild(item)
        xml.appendChild(articles)
        return xml

    def add_article(self, title=None, desc=None, pic_url=None, url=None):
        content = {
            self.tag_title: title,
            self.tag_description: desc,
            self.tag_pic_url: pic_url,
            self.tag_url: url
        }
        self.article_list.append(content)