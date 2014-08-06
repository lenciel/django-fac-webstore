#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import OrderedDict
import logging
import os

from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.safestring import SafeString

from apps import foundation
from apps.cms.models import Article
from apps.common.models import BaseModel, ActiveDataManager
from apps.foundation.models import Image


logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


SUMMARY_SHORT_WORDS = 50


class Provider(BaseModel):
    name = models.CharField(max_length=128,
                            verbose_name=u'名称',
                            unique=True)

    description = models.TextField(max_length=512,
                                   verbose_name=u'描述')

    online_service = models.CharField(max_length=512,
                                      default='',
                                      blank=True,
                                      verbose_name=u'在线客服')

    phone_service = models.CharField(max_length=64,
                                     default='',
                                     blank=True,
                                     verbose_name=u'电话客服')

    email = models.CharField(max_length=64,
                             default='',
                             blank=True,
                             verbose_name=u'邮箱')

    def is_deletable(self):
        return not self.products_count()

    def products_count(self):
        return self.products.count()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'供应商'
        verbose_name_plural = verbose_name


class ContentToImage(models.Model):
    """
    中间关系model. 记录content和image的关系.
    """
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

    image = models.ForeignKey(Image, verbose_name=u'关联图片')
    display_order = models.PositiveIntegerField(verbose_name=u'显示顺序',
                                                default=0)

    def __unicode__(self):
        return unicode(self.image)

    def image_url(self):
        return self.image.url()

    def image_width(self):
        return self.image.width

    def image_height(self):
        return self.image.height

    class Meta:
        ordering = ('display_order',)
        abstract = True


class ProductImage(ContentToImage):
    pass


class ProductDetailImage(ContentToImage):
    pass


class ProductCategory(models.Model):
    name = models.CharField(max_length=16,
                            unique=True,
                            verbose_name=u'名称')

    def active_attributes(self):
        return self.attributes.filter(is_active=True).order_by('display_order', 'name')

    def attribute_names(self):
        return ", ".join([attribute.name for attribute in self.active_attributes()])

    def is_deletable(self):
        return not self.attributes_count()

    def attributes_count(self):
        return self.attributes.count()

    def get_attribute_max_display_order(self):
        try:
            return self.attributes.latest().display_order
        except ProductCategoryAttribute.DoesNotExist:
            return 0

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = u'商品类别'
        verbose_name_plural = verbose_name


class ProductCategoryAttribute(models.Model):
    name = models.CharField(max_length=64,
                            verbose_name=u'属性名称')

    category = models.ForeignKey(ProductCategory,
                                 verbose_name=u'类别',
                                 related_name='attributes')

    display_order = models.IntegerField(default=0,
                                        verbose_name='显示顺序')

    description = models.TextField(max_length=128,
                                   verbose_name=u'描述',
                                   default="",
                                   blank=True)

    is_active = models.BooleanField(default=True,
                                    verbose_name=u'激活状态')

    objects = models.Manager()

    active_objects = ActiveDataManager()

    def is_deletable(self):
        return not self.options_count()

    def options_count(self):
        return ProductAttributeOption.objects.filter(attribute=self).count()

    def __unicode__(self):
        return "%s-%s" % (self.category.name, self.name)

    class Meta:
        ordering = ('category', 'display_order', 'name',)
        verbose_name = u'商品属性'
        verbose_name_plural = verbose_name
        unique_together = ('category', 'name')
        get_latest_by = 'display_order'


class Product(BaseModel):
    name = models.CharField(max_length=128,
                            verbose_name=u'名称',
                            unique=True)

    title_image_file = models.ImageField(upload_to=foundation.models.unique_image_name,
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

    summary = models.CharField(max_length=200,
                               verbose_name=u'摘要',
                               default='',
                               blank=True)

    provider = models.ForeignKey(Provider,
                                 verbose_name=u'供应商',
                                 related_name='products')

    category = models.ForeignKey(ProductCategory,
                                 verbose_name=u'商品类别',
                                 related_name='products')

    images = generic.GenericRelation(ProductImage,
                                     blank=True,
                                     null=True,
                                     verbose_name=u'商品图片集',
                                     related_name='products',
                                     help_text=u'用户可以看到的商品展示图集，比如应用抓图、产品照片等')

    is_published = models.BooleanField(default=False,
                                       verbose_name=u'是否已发布')

    rating = models.DecimalField(max_digits=10,
                                 decimal_places=1,
                                 verbose_name=u'评分',
                                 default=1.0)

    sale_volume = models.PositiveIntegerField(verbose_name=u'销量',
                                              default=0)

    price = models.DecimalField(max_digits=16,
                                decimal_places=2,
                                verbose_name=u'价格',
                                default=0.0)

    price_text = models.CharField(max_length=100,
                                  verbose_name=u'价格文本',
                                  default='',
                                  blank=True)

    attributes = models.ManyToManyField(ProductCategoryAttribute,
                                        through='ProductAttributeOption',
                                        verbose_name=u'属性集')

    detail_images = generic.GenericRelation(ProductDetailImage,
                                            blank=True,
                                            null=True,
                                            verbose_name=u'详情图片集',
                                            help_text=u'和"图集"不同的是，这是在产品详情的一部分，后台可以把ppt、表格、资料等以图片形式展示')

    # 是没有特殊效果的plain text
    detail_text = models.TextField(verbose_name=u'详情文本',
                                   default='')

    web_link = models.URLField(max_length=255,
                               verbose_name=u'商品链接',
                               default='',
                               blank=True)

    article = models.ForeignKey(Article,
                                verbose_name=u'导购文章',
                                null=True,
                                blank=True,
                                related_name='products')

    is_pinned = models.BooleanField(default=False,
                                    blank=True,
                                    verbose_name=u'静态显示')

    STATUS_OK = 0
    STATUS_DELETE = -1

    def status(self):
        return self.STATUS_OK if self.is_published and self.is_active else self.STATUS_DELETE

    def images_html(self):
        html = ""
        for image in self.images.all().order_by('display_order'):
            html += '<img src="%s"></img>' % image.image_url()
        return SafeString(html)

    def detail_images_html(self):
        html = ""
        for image in self.detail_images.all().order_by('display_order'):
            html += '<img src="%s"></img>' % image.image_url()
        return SafeString(html)

    def title_image_url(self):
        return settings.STATIC_DEFAULT_TITLE_IMAGE_URL if not self.title_image_file else self.title_image_file.url

    def get_samplecase_max_display_order(self):
        try:
            return self.samplecases.latest().display_order
        except SampleCase.DoesNotExist:
            return 0

    def get_options_and_skus(self):
        attribute_options = OrderedDict()
        option_values = {}
        # get the option values grouped by attribute
        for option in self.attribute_options.all():
            option_value = {"id": option.id, "value": option.value, "paired_option_ids": set(), "exclude_option_ids": set()}
            option_values[option.id] = option_value
            if option.attribute.name in attribute_options:
                attribute_options[option.attribute.name].append(option_value)
            else:
                attribute_options[option.attribute.name] = [option_value]

        # sku information include price
        sku_list = {}
        # only show full stock sku
        for sku in self.skus.all():
            sku_list[sku.get_clean_options()] = {"price": float(sku.price), "sku_id": sku.id, "is_outofstock": sku.is_outofstock()}
            option_ids = sku.get_option_ids()
            # 计算每个option允许的组合
            for id in option_ids:
                option_values[id]["paired_option_ids"] |= set(option_ids)
            if sku.is_outofstock():
                for id in option_ids:
                    option_values[id]["exclude_option_ids"] |= set(option_ids)

        # clean up no-paired option
        # the data in attribute_options like below
        # {"颜色": [{"id": 1, "value":"红", "paired_option_ids":[1,2], "exclude_option_ids":[]},
        #           {"id": 2, "value":"黑", "paired_option_ids":[1,3], "exclude_option_ids":[]}],
        #  "规格":  [{"id": 3, "value":"大", "paired_option_ids":[4], "exclude_option_ids":[]}]}
        for key, option_values in attribute_options.items():
            attribute_options[key] = [option_value for option_value in option_values if option_value['paired_option_ids']]
        return attribute_options, sku_list

    def get_absolute_url(self):
        return reverse('website:product:product_detail', args=[str(self.id)])

    def is_deletable(self):
        return not (self.options_count() or self.skus_count())

    def options_count(self):
        return ProductAttributeOption.objects.filter(product=self).count()

    def skus_count(self):
        return self.skus.count()

    def summary_short(self):
        return self.summary[0:SUMMARY_SHORT_WORDS] + (u"..." if len(self.summary) > SUMMARY_SHORT_WORDS else "")

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'商品'
        verbose_name_plural = verbose_name


class SampleCase(models.Model):
    title = models.CharField(max_length=128,
                             verbose_name=u'标题')

    product = models.ForeignKey(Product,
                                verbose_name=u'产品',
                                related_name='samplecases')

    title_image_file = models.ImageField(upload_to=foundation.models.unique_image_name,
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

    display_order = models.PositiveIntegerField(verbose_name=u'显示顺序',
                                                default=0)

    # 是没有特殊效果的plain text
    detail_text = models.TextField(verbose_name=u'详情文本',
                                   default='')

    def __unicode__(self):
        return self.title

    def title_image_url(self):
        return settings.STATIC_DEFAULT_TITLE_IMAGE_URL if not self.title_image_file else self.title_image_file.url

    class Meta:
        verbose_name = u'商品案例'
        verbose_name_plural = verbose_name
        ordering = ('display_order', )
        get_latest_by = 'display_order'


class ProductAttributeOption(models.Model):
    product = models.ForeignKey(Product,
                                verbose_name=u'产品',
                                related_name='attribute_options')

    attribute = models.ForeignKey(ProductCategoryAttribute,
                                  verbose_name=u'属性')

    value = models.CharField(max_length=64,
                             verbose_name=u'属性值')

    display_order = models.PositiveIntegerField(verbose_name=u'显示顺序',
                                                default=0)

    def __unicode__(self):
        return u"%s-%s-%s" % (unicode(self.product), unicode(self.attribute), self.value)

    def is_deletable(self):
        return not self.used_by_skus()

    def used_by_skus(self):
        return ProductSku.objects.filter(product=self.product).filter(attribute_options__icontains=(',%d,' % self.id))\
            .count() > 0

    class Meta:
        verbose_name = u'商品属性值'
        verbose_name_plural = verbose_name
        unique_together = ('product', 'attribute', 'value')
        get_latest_by = 'display_order'
        ordering = ['display_order']


class ProductSku(models.Model):
    product = models.ForeignKey(Product,
                                verbose_name=u'产品',
                                related_name='skus')

    sku = models.CharField(max_length=64,
                           verbose_name='SKU',
                           blank=True,
                           default="")

    # ProductAttributeOption数据id,按照","分割. 比如:
    #  123,456,789
    attribute_options = models.CharField(max_length=128,
                                         verbose_name='属性组合')

    price = models.DecimalField(max_digits=16,
                                decimal_places=2,
                                verbose_name=u'价格',
                                default=0.0)

    stock_quantity = models.PositiveIntegerField(verbose_name=u'库存量',
                                                 default=1)

    def display_text(self):
        text = ""
        for option in self.product.attribute_options.filter(id__in=self.get_option_ids()):
            if not text:
                text = option.value
            else:
                text += " x " + option.value
        return self.product.name + " " + text

    def __unicode__(self):
        return u"%s-%.2f" % (self.sku, float(self.price))

    def set_options(self, opt_ids):
        # Braces id with ',' to group '5,' and '15,' etc.
        self.attribute_options = ",%s," % ",".join(opt_ids)

    def get_selected_options(self, options):
        return set(self.attribute_options.split(',')) & set([str(o.id) for o in options])

    def get_option_ids(self):
        return [int(item) for item in self.attribute_options.strip(',').split(',')]

    def get_clean_options(self):
        return self.attribute_options.strip(',')

    def is_deletable(self):
        return not self.orders_count()

    def orders_count(self):
        from apps.order.models import OrderSku
        return OrderSku.objects.filter(sku=self).count()

    def is_outofstock(self):
        return self.stock_quantity <= 0

    class Meta:
        # 商品SKU(stock keep unit)是针对商品属性值的组合
        verbose_name = u'商品SKU'
        verbose_name_plural = verbose_name
