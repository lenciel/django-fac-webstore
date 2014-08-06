#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import os
import urllib2

from django.core.management import BaseCommand
from apps.wechat.menu import WeChatMenu
from apps.wechat.models import WeChatProfile

logger = logging.getLogger('apps.'+os.path.basename(os.path.dirname(__file__)))
log_tag = 'Sync WeChat Menu: '


class Command(BaseCommand):

    def handle(self, *args, **options):
        # sync the structure of the menu to wechat server,
        # the structure is described as json data in WeChatMenu.
        access_token = WeChatProfile.objects.get_access_token()
        try:
            response = urllib2.urlopen(
                url='https://api.weixin.qq.com/cgi-bin/menu/create?access_token={0}'.format(access_token),
                data=WeChatMenu.build_as_json().encode(encoding='utf-8'))
            response_dict = json.loads(response.read())
            err_code = response_dict['errcode']
            err_msg = response_dict['errmsg']

            if err_code == 0 and err_msg == 'ok':
                logger.info(log_tag + 'Update successfully.')
            else:
                logger.error(log_tag + 'Failed with errcode:{0} errmsg:{1}'.format(err_code, err_msg))

        except urllib2.HTTPError, e:
                logger.error(log_tag + 'HTTPError = ' + str(e.code))
        except urllib2.URLError, e:
                logger.error(log_tag + 'URLError = ' + str(e.reason))
        except ValueError:
                logger.error(log_tag + 'Failed due to invalid response data.')
