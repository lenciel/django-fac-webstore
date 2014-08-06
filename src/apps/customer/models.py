#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os

from django.db import models
from django.contrib.auth import get_user_model
from apps.account.models import User

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


class Customer(User):
    is_company = models.BooleanField(verbose_name=u'是否企业用户')

    company_name = models.CharField(max_length=128,
                                    verbose_name=u'企业名称')

    company_address = models.CharField(max_length=128,
                                       verbose_name=u'企业地址')

    company_tel = models.CharField(max_length=32,
                                   verbose_name=u'企业固话',
                                   null=True,
                                   blank=True,
                                   default="")

    company_website = models.URLField(verbose_name=u'公司网页',
                                      null=True,
                                      blank=True,
                                      default="")

    company_industry = models.CharField(max_length=32,
                                        verbose_name=u'公司行业',
                                        null=True,
                                        blank=True,
                                        default="")

    class Meta:
        verbose_name = u'消费用户'
        verbose_name_plural = verbose_name
        permissions = (
            ("view_customer", "查看消费用户"),
        )


class Address(models.Model):
    receiver = models.CharField(verbose_name=u'收货人',
                                max_length=32)

    address = models.CharField(verbose_name=u'详细地址',
                               max_length=128)
    address_province = models.CharField(verbose_name=u'省',
                                        max_length=16)
    address_city = models.CharField(verbose_name=u'城市',
                                    max_length=16)
    address_district = models.CharField(verbose_name=u'区域',
                                        max_length=32)

    mobile = models.CharField(verbose_name=u'手机号码',
                              max_length=32)
    tel = models.CharField(verbose_name=u'固定电话',
                           max_length=32,
                           default="",
                           blank=True)
    email = models.EmailField(verbose_name=u'邮箱',
                              default="",
                              blank=True)

    def to_json(self):
        return {"receiver": self.receiver, "address":self.address, "address_province":self.address_province,
                "address_city": self.address_city, "address_district": self.address_district,
                "mobile": self.mobile, "tel": self.tel, "email": self.email}

    def display_text(self):
        return u"%s %s%s%s%s %s" % (self.receiver, self.address_province, self.address_city, self.address_district,
                                    self.address, self.mobile)

    class Meta:
        abstract = True


class ShipAddress(Address):
    owner = models.ForeignKey(Customer,
                              verbose_name=u'消费用户',
                              related_name="ship_addresses")

    is_default = models.BooleanField(verbose_name='默认收货地址',
                                     default=False)

    created = models.DateTimeField(verbose_name=u'创建时间',
                                   auto_now_add=True)

    def to_json(self):
        json = super(ShipAddress, self).to_json()
        json['is_default'] = self.is_default
        return json

    def __unicode__(self):
        return self.address

    class Meta:
        verbose_name = u'送货地址'
        verbose_name_plural = verbose_name
        ordering = ('created',)

