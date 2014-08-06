#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from django.utils import timezone


class ActiveDataManager(models.Manager):
    def get_query_set(self):
        return super(ActiveDataManager, self).get_query_set().filter(is_active=True)


class BaseModel(models.Model):

    created = models.DateTimeField(verbose_name=u'创建时间',
                                   auto_now_add=True)

    updated = models.DateTimeField(verbose_name=u'更新时间',
                                   auto_now=True)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              verbose_name=u'负责人',
                              related_name='+',
                              null=True)

    creator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                verbose_name=u'创建人',
                                related_name='+')

    is_active = models.BooleanField(default=True,
                                    verbose_name=u'激活状态')

    objects = models.Manager()

    active_objects = ActiveDataManager()

    def created_at_timestamp(self):
        return int(timezone.localtime(self.created_at).strftime("%s"))

    def updated_at_timestamp(self):
        return int(timezone.localtime(self.updated_at).strftime("%s"))


    class Meta:
        abstract = True
