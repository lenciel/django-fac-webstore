#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from django.conf import settings
from django.db import models
from apps.common.models import ActiveDataManager
from utils import random

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


def unique_image_name(instance, filename):
    try:
        ext = os.path.splitext(filename)[1].lstrip('.')
    except BaseException:
        ext = "jpg"
    return '%s/%s' % (settings.MEDIA_IMAGE_PREFIX, random.gen_uuid_filename(ext))


class ImageManager(models.Manager):

    def get_all_for_names(self, image_names):
        return self.get_query_set().filter(image_file__in=['%s/%s' % (settings.MEDIA_IMAGE_PREFIX, name) for name in image_names])


class Image(models.Model):
    """
    图片链接. 只允许添加和删除, 不允许修改. 修改的图片会创建全新的一条记录.
    """

    image_file = models.ImageField(upload_to=unique_image_name,
                                   db_index=True,
                                   verbose_name=u'图片',
                                   width_field='width',
                                   height_field='height')

    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name=u"创建日期")

    width = models.PositiveIntegerField(verbose_name='图片宽度',
                                        null=True,
                                        blank=True,
                                        default=0)
    height = models.PositiveIntegerField(verbose_name='图片长度',
                                         null=True,
                                         blank=True,
                                         default=0)

    objects = ImageManager()

    def url(self):
        return self.image_file.url

    def __unicode__(self):
        return self.url()

    class Meta:
        verbose_name = u'图片'
        verbose_name_plural = verbose_name
