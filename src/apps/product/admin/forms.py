#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import re

from django.core.urlresolvers import reverse
from django import forms
from django.forms.models import BaseInlineFormSet

from apps.common.ace import AceClearableFileInput, AceBooleanField
from apps.common.admin.datatables import DatatablesIdColumn, DatatablesBuilder, DatatablesImageColumn, DatatablesTextColumn,\
    DatatablesBooleanColumn, DatatablesUserChoiceColumn, DatatablesDateTimeColumn, DatatablesColumnActionsRender,\
    DatatablesActionsColumn, DatatablesModelChoiceColumn
from apps.foundation.models import Image
from apps.product.models import Product, Provider, ProductCategory, ProductImage, ProductDetailImage, SampleCase,\
    ProductCategoryAttribute, ProductAttributeOption, ProductSku


HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))

PERM_EDIT_PRODUCT = 'product.change_product'


class ProductForm(forms.ModelForm):
    images_html = forms.CharField(label=u'商品图片集',
                                  widget=forms.Textarea(),
                                  required=False)

    detail_images_html = forms.CharField(label=u'详情图片集',
                                         widget=forms.Textarea(),
                                         required=False)
    #包含raw text + image tag
    # we only concern the "img" tag and strip others
    images_plain_text = forms.CharField(label=u'商品图片集plain文本内容(隐藏)',
                                        widget=forms.HiddenInput())

    detail_images_plain_text = forms.CharField(label=u'详情图片集plain文本内容(隐藏)',
                                               widget=forms.HiddenInput())

    is_pinned = AceBooleanField(required=False,
                                label=u'静态显示')

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = "required input-xxlarge limited"
        self.fields['summary'].widget.attrs['class'] = "limited col-md-10"
        self.fields['detail_text'].widget.attrs['class'] = "input-xxlarge"
        self.fields['images_html'].help_text = self.Meta.model._meta.get_field('images').help_text
        self.fields['detail_images_html'].help_text = self.Meta.model._meta.get_field('detail_images').help_text
        self.fields['web_link'].widget.attrs['class'] = "col-md-12"
        self.fields['provider'].queryset = Provider.active_objects.only('name')

    def clean(self):
        cleaned_data = super(ProductForm, self).clean()
        # keep the old image and delete it if changed at save()
        self.old_title_image_file = self.instance.title_image_file
        return cleaned_data

    def save(self, commit=False):
        product = super(ProductForm, self).save(commit)
        if not hasattr(product, "creator"):
            product.creator = self.initial['request'].user
            product.owner = product.creator

        if self.old_title_image_file and self.old_title_image_file != self.instance.title_image_file:
            os.unlink(self.old_title_image_file.path)
        product.save()

        ProductForm.handle_images(product, ProductImage, self.cleaned_data['images_html'],
                                  lambda: product.images.clear())
        ProductForm.handle_images(product, ProductDetailImage, self.cleaned_data['detail_images_html'],
                                  lambda: product.detail_images.clear())

        return product

    @staticmethod
    def handle_images(model, image_model, images_text, clear):
        image_names = ProductForm.extract_images(images_text)
        images = Image.objects.get_all_for_names(image_names)
        display_order = 0
        clear()
        # NOTE: can't ensure the order fetching from db is match to image_names's order
        # so should loop image_names one by one
        for image_name in image_names:
            for image in images:
                if image.url().endswith(image_name):
                    image_model.objects.create(content_object=model, image=image, display_order=display_order)
                    display_order += 1

    image_re = re.compile(r'<img src=".*?/images/(.*?)"')

    @staticmethod
    def extract_images(content_plain_text):
        # the text content like below. I will extract the name from it
        #   's1s2<img src="/media/images/726d31924b094735b44c1af27ffe37ce.png" _src="/media/images/726d31924b094735b44c1af27ffe37ce.png">s3'
        return ProductForm.image_re.findall(content_plain_text)


    class Meta:
        model = Product
        fields = ('name', 'title_image_file', 'provider', 'web_link', 'price_text', 'summary', 'category', 'rating', 'sale_volume', 'images_html',
                  'detail_text', 'detail_images_html', 'is_pinned')

        widgets = {
            'title_image_file': AceClearableFileInput(),
        }


class ProductDatatablesBuilder(DatatablesBuilder):
    id = DatatablesIdColumn()

    name = DatatablesTextColumn(label='名称',
                                is_searchable=True)

    title_image_url = DatatablesImageColumn(label='标题图片')

    summary = DatatablesTextColumn(label='摘要',
                                   is_searchable=True)

    provider = DatatablesModelChoiceColumn(label='服务商',
                                           is_searchable=True,
                                           col_width="8%",
                                           queryset=Provider.active_objects.filter(is_active=True).order_by('name'))

    category = DatatablesModelChoiceColumn(label='商品类别',
                                           is_searchable=True,
                                           col_width="8%",
                                           queryset=ProductCategory.objects.all())

    is_published = DatatablesBooleanColumn((('', u'全部'), (1, u'发布'), (0, u'草稿')),
                                           label='状态',
                                           is_searchable=True,
                                           col_width='7%',
                                           render=(lambda request, model, field_name:
                                                   u'<span class="label label-info"> 发布 </span>'
                                                   if model.is_published else
                                                   u'<span class="label label-warning"> 草稿 </span>'))

    is_pinned = DatatablesBooleanColumn(label='静态显示',
                                        col_width="5%",
                                        is_sortable=True,)

    creator = DatatablesUserChoiceColumn(label=u'作者',)

    updated = DatatablesDateTimeColumn(label=u'修改时间')

    def actions_render(request, model, field_name):
        action_url_builder = lambda model, action: reverse('admin:product:product_update', kwargs={'pk': model.id, 'action_method': action})

        if model.is_published:
            actions = [{'is_link': False, 'name': 'cancel', 'text': u'撤销', 'icon': 'icon-cut', "url": action_url_builder(model, "cancel")}]
        else:
            actions = [{'is_link': True, 'name': 'edit', 'text': u'编辑', 'icon': 'icon-edit'},
                       {'is_link': True, 'name': 'edit', 'text': u'案例', 'icon': 'icon-pencil', "url_name": "admin:product:product_samplecases_edit"},
                       {'is_link': True, 'name': 'edit', 'text': u'属性值', 'icon': 'icon-asterisk', "url_name": "admin:product:product_attribute_options_edit"},
                       {'is_link': False, 'name': 'delete', 'text': u'删除', 'icon': 'icon-remove'},
                       {'is_link': False, 'name': 'publish', 'text': u'发布', 'icon': 'icon-save', "url": action_url_builder(model, "publish")},]
            if model.options_count():
                actions += [{'is_link': True, 'name': 'edit', 'text': u'SKU', 'icon': 'icon-money', "url_name": "admin:product:product_sku_edit"},]
        actions.append({'is_link': False, 'name': 'preview', 'text': u'预览', 'icon': 'icon-eye-open', 'handler_type': 'customize',
                        'url': reverse('website:product:product_preview', kwargs={'pk': model.id}) })
        return DatatablesColumnActionsRender(actions=actions, action_permission=PERM_EDIT_PRODUCT).render(request, model, field_name)

    _actions = DatatablesActionsColumn(render=actions_render)

HTTP_PROTOCOL = 'http://'
HTTPS_PROTOCOL = 'https://'


class ProviderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProviderForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = "required input-xlarge limited"
        self.fields['description'].widget.attrs['class'] = "limited input-xxlarge"
        self.fields['online_service'].widget.attrs['class'] = "limited input-xxlarge"

    def clean_online_service(self):
        online_service = self.cleaned_data.get('online_service')
        if not online_service:
            return online_service
        if not (online_service.startswith(HTTP_PROTOCOL) or online_service.startswith(HTTPS_PROTOCOL)):
            online_service = HTTP_PROTOCOL + online_service
        return online_service

    def save(self, commit=False):
        provider = super(ProviderForm, self).save(commit)
        if not hasattr(provider, "creator"):
            provider.creator = self.initial['request'].user
            provider.owner = self.initial['request'].user
        provider.save()
        return provider

    class Meta:
        model = Provider
        fields = ('name', 'description', 'online_service', 'phone_service', 'email')


class ProviderDatatablesBuilder(DatatablesBuilder):
    id = DatatablesIdColumn()

    name = DatatablesTextColumn(label='名称',
                                is_searchable=True)

    def actions_render(request, model, field_name):
        actions = [{'is_link': True, 'name': 'edit', 'text': u'编辑', 'icon': 'icon-edit'},
                   {'is_link': False, 'name': 'delete', 'text': u'删除', 'icon': 'icon-remove'}]
        return DatatablesColumnActionsRender(actions=actions, action_permission=PERM_EDIT_PRODUCT).render(request, model, field_name)

    _actions = DatatablesActionsColumn(render=actions_render)


class ProductCategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductCategoryForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = "required input-xlarge limited"
        self.fields['name'].widget.attrs['data-regex'] = r'^\S+$'

    class Meta:
        model = ProductCategory
        fields = ('name', )


class ProductCategoryDatatablesBuilder(DatatablesBuilder):
    id = DatatablesIdColumn()

    name = DatatablesTextColumn(label=u'名称',
                                is_searchable=True)

    attribute_names = DatatablesTextColumn(label=u'属性')

    def actions_render(request, model, field_name):
        actions = [{'is_link': True, 'name': 'edit', 'text': u'编辑', 'icon': 'icon-edit'},
                   {'is_link': True, 'name': 'edit', 'text': u'属性', 'icon': 'icon-pencil', "url_name": "admin:product:productcategory_attributes_edit"},
                   {'is_link': False, 'name': 'delete', 'text': u'删除', 'icon': 'icon-remove'},]
        return DatatablesColumnActionsRender(actions=actions, action_permission=PERM_EDIT_PRODUCT).render(request, model, field_name)

    _actions = DatatablesActionsColumn(render=actions_render)


class SampleCaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SampleCaseForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = "required col-md-12 limited"
        self.fields['detail_text'].widget.attrs['class'] = "col-md-12 required"
        self.fields['title_image_file'].widget = AceClearableFileInput()

    def clean(self):
        cleaned_data = super(SampleCaseForm, self).clean()
        # keep the old image and delete it if changed at save()
        self.old_image_file = self.instance.title_image_file
        return cleaned_data

    def save(self, commit=False):
        samplecase = super(SampleCaseForm, self).save(commit)
        if self.old_image_file and self.old_image_file != self.instance.title_image_file:
            os.unlink(self.old_image_file.path)
        # set the order to the max one + 1 if it's new section
        if self.cleaned_data.get('ORDER') is None:
            samplecase.display_order = self.cleaned_data['product'].get_samplecase_max_display_order() + 1
        else:
            samplecase.display_order = self.cleaned_data['ORDER']
        samplecase.save()
        return samplecase

    class Meta:
        model = SampleCase
        fields = ('title', 'title_image_file', 'detail_text')


class ProductCategoryAttributeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductCategoryAttributeForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = "required col-md-12 limited"
        self.fields['description'].widget.attrs['class'] = "col-md-12"

    def save(self, commit=False):
        attribute = super(ProductCategoryAttributeForm, self).save(commit)
        # set the order to the max one + 1 if it's new section
        if self.cleaned_data.get('ORDER') is None:
            logger.debug(str(self.cleaned_data))
            attribute.display_order = self.cleaned_data['category'].get_attribute_max_display_order() + 1
        else:
            attribute.display_order = self.cleaned_data['ORDER']
        attribute.save()
        return attribute

    class Meta:
        model = ProductCategoryAttribute
        fields = ('name', 'description')


class ProductAttributeOptionFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(ProductAttributeOptionFormSet, self).__init__(*args, **kwargs)

        for form in self.forms:
            form.fields['attribute'].queryset = ProductCategoryAttribute.active_objects.filter(category=self.instance.category)


class ProductAttributeOptionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductAttributeOptionForm, self).__init__(*args, **kwargs)
        #product = self.initial.get('parent')
        self.fields['value'].widget.attrs['class'] = "required col-md-12 limited"

    class Meta:
        model = ProductAttributeOption
        fields = ('attribute', 'value')


ATTR_REGEX = re.compile('.*attr_\d+$')


class ProductSkuForm(forms.ModelForm):
    class Meta:
        model = ProductSku
        fields = ('sku', 'price', 'stock_quantity')

    def save(self, commit=True):
        opt_ids = [v for k, v in self.cleaned_data.items() if ATTR_REGEX.match(k)]
        self.instance.set_options(opt_ids)
        return super(ProductSkuForm, self).save(commit)


class ProductSkuFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(ProductSkuFormSet, self).__init__(*args, **kwargs)
        attr_options = ProductAttributeOption.objects.filter(product=self.instance)
        attr_opt_map = {}
        for opt in attr_options:
            options = attr_opt_map.setdefault(opt.attribute, [])
            options.append(opt)
        for form in self.forms:
            for k, v in attr_opt_map.items():
                form.fields['attr_%d' % k.id] = forms.ChoiceField(label=k.name,
                                                                  choices=[(o.id, o.value) for o in v])
                selected_value = form.instance.get_selected_options(v)
                if selected_value:
                    form.fields['attr_%d' % k.id].initial = selected_value.pop()

    def save(self, commit=True):
        lowest_price = 0
        if self.cleaned_data:
            lowest_price = min([x['price'] for x in self.cleaned_data])
        # 设置product.price为sku的最低价格
        self.instance.price = lowest_price
        self.instance.save()

        return super(ProductSkuFormSet, self).save(commit)