#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import time
from django.core.management import BaseCommand
from django.conf import settings
from apps.wechat.client import WeChatClient
from apps.wechat.models import WeChatProfile

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


class Command(BaseCommand):
    """
    run this command in crontab when start server.
    sample: crontab */2 * * * * python manage.py updatetoken
    """
    def handle(self, *args, **options):
        # 在失效之前就要提前更新access token
        time_to_check = time.time() + settings.WECHAT_TIME_TO_REFRESH_BEFORE_ACCESS_TOKEN_EXPIRE_IN_SECONDS
        if WeChatProfile.objects.is_access_token_expired(time_to_check):
            WeChatClient.refresh_token()