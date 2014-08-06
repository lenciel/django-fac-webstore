#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from django.core.urlresolvers import reverse
from django.utils import timezone
import os
from django.conf import settings
from django.db import models
from apps.common.models import BaseModel
from apps.foundation.models import unique_image_name
from utils import random

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


def unique_html_name(instance, filename):
    return '%s/%s' % (settings.MEDIA_CONTENT_PREFIX, random.gen_uuid_filename('html'))


class Article(BaseModel):
    title = models.CharField(max_length=128,
                             verbose_name=u'标题')
    title_image_file = models.ImageField(upload_to=unique_image_name,
                                         blank=True,
                                         null=True,
                                         verbose_name=u'标题图片',
                                         width_field='title_image_width',
                                         height_field='title_image_height')
    title_image_width = models.PositiveIntegerField(verbose_name='标题图片宽度',
                                                    null=True,
                                                    blank=True,
                                                    default=0)
    title_image_height = models.PositiveIntegerField(verbose_name='标题图片长度',
                                                     null=True,
                                                     blank=True,
                                                     default=0)

    content_file = models.FileField(upload_to=unique_html_name,
                                    verbose_name=u'html文件')

    DEFAULT_SOURCE = u'应用工厂'
    source = models.CharField(max_length=128,
                              verbose_name=u'资讯来源',
                              blank=True,
                              default=DEFAULT_SOURCE)

    summary = models.CharField(max_length=200,
                               verbose_name=u'摘要',
                               default='',
                               blank=True)

    is_published = models.BooleanField(default=False,
                                       verbose_name=u'是否已发布')

    def published_at_timestamp(self):
        return int(timezone.localtime(self.published_at).strftime("%s")) if self.published_at else 0

    def title_image_url(self):
        return settings.STATIC_DEFAULT_TITLE_IMAGE_URL if not self.title_image_file else self.title_image_file.url

    SUMMARY_LENGTH = 64

    def __unicode__(self):
        return self.title

    STATUS_OK = 0
    STATUS_DELETE = -1

    def status(self):
        return self.STATUS_OK if self.is_published and self.is_active else self.STATUS_DELETE

    def content_url(self):
        return self.content_file.url

    def content_html(self):
        try:
            with open(self.content_file.path) as f:
                html = f.read()
        except IOError:
            html = u'无内容'
        return html

    def content_short_url(self):
        """
        a short content_url
        """
        return reverse("article_html", kwargs={'pk': self.id})

    def __unicode__(self):
        return self.summary

    class Meta:
        verbose_name = u"资讯"
        permissions = (('view_article', u'查看资讯'),)

