#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import os
import urllib2
from django.conf import settings
import time
from apps.wechat.models import WeChatProfile

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


class WeChatClient(object):
    SUCCESS = 0
    BAD_APP_SECRET = 40001
    ILLEGAL_OPENID = 40003

    @staticmethod
    def post_text_message(openid, text):
        # 发送消息给微信用户
        """
        {
            "touser":"OPENID",
            "msgtype":"text",
            "text":
            {
                "content":"Hello World"
            }
        }
        参数	             是否必须	       说明
        access_token	 是	        调用接口凭证
        touser	         是	        普通用户openid
        msgtype	         是	        消息类型，text
        content	         是	        文本消息内容
        """
        access_token = WeChatProfile.objects.get_access_token()
        if not access_token or not openid:
            return
        url = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={0}'.format(access_token)
        text_content = dict()
        text_content['content'] = text

        post_data = dict()
        post_data['touser'] = openid
        post_data['msgtype'] = "text"
        post_data['text'] = text_content

        response = None
        try:
            req = urllib2.urlopen(url, json.dumps(post_data))
            response = req.read()
            response_dict = json.loads(response)
            err = response_dict['errcode']
            if err == WeChatClient.SUCCESS:
                return
            elif err == WeChatClient.BAD_APP_SECRET:
                logger.error('post wechat text message failed: bad access token')
            elif err == WeChatClient.ILLEGAL_OPENID:
                logger.error('post wechat text message failed: bad open id')
            else:
                logger.error('post wechat text message failed: {0}', err)
        except urllib2.HTTPError, e:
            logger.error('refresh_access_token: HTTPError = ' + str(e.code))
        except ValueError:
            logger.error('refresh_access_token: Value Error. response = {0}', response)

    @staticmethod
    def refresh_token():
        """
        正常情况下，微信会返回下述JSON数据包给公众号：
        {"access_token":"ACCESS_TOKEN","expires_in":7200}
        参数	说明
        access_token	 获取到的凭证
        expires_in	 凭证有效时间，单位：秒
        错误时微信会返回错误码等信息，JSON数据包示例如下（该示例为AppID无效错误）:
        {"errcode":40013,"errmsg":"invalid appid"}
        """
        try:
            url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}' \
                .format(settings.WECHAT_APPID, settings.WECHAT_SECRET)

            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
            response_dict = json.loads(response.read())
            WeChatProfile.objects.refresh_access_token(response_dict['access_token'], time.time()+response_dict['expires_in'])
        except urllib2.HTTPError, e:
            logger.error('refresh_access_token: HTTPError = ' + str(e.code))
        except urllib2.URLError, e:
            logger.error('refresh_access_token: URLError = ' + str(e.reason))
        except ValueError:
            logger.error('refresh_access_token: ValueError')