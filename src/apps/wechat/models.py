#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from django.db import models

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


class WeChatProfileManager(models.Manager):
    def get_access_token(self):
        return self.current_token().access_token

    def refresh_access_token(self, access_token, expires_at):
        t = self.current_token()
        t.access_token = access_token
        t.expires_at = expires_at
        t.save()

    def is_access_token_expired(self, at_time):
        return self.current_token().expires_at < at_time

    def clean_access_token(self):
        t = self.current_token()
        t.expires_at = -1
        t.save()

    def current_token(self):
        return self.all()[0]


class WeChatProfile(models.Model):
    access_token = models.CharField(max_length=200)
    expires_at = models.FloatField(default=-1)
    objects = WeChatProfileManager()


class WeChatUserManager(models.Manager):
    def get_bound_user(self, openid):
        try:
            return self.get(openid=openid, customer__isnull=False)
        except WeChatUser.DoesNotExist:
            return None


class WeChatUser(models.Model):
    customer = models.OneToOneField("customer.Customer",
                                    verbose_name=u'账户名',
                                    null=True)

    openid = models.CharField(verbose_name=u'openid',
                              max_length=128)

    created_at = models.DateTimeField(verbose_name=u'创建时间',
                                      auto_now_add=True)

    # start search time, user will have 60 seconds to input keyword.
    start_search_at = models.PositiveIntegerField(verbose_name=u'开始搜索时间',
                                                  default=0)

    objects = WeChatUserManager()