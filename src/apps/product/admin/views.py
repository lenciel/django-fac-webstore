#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from django.forms.models import inlineformset_factory
from apps.common.admin.views import AjaxSimpleUpdateView, ModelAwareMixin, RequestAwareMixin,\
    NavigationHomeMixin, DatatablesBuilderMixin, AjaxListView, AjaxCreateView, AjaxUpdateView, AjaxDatatablesView, ModelActiveView,\
    AjaxFormsetEditView, PermissionRequiredMixin
from .forms import ProductForm, ProductDatatablesBuilder, ProviderForm, ProviderDatatablesBuilder, ProductCategoryForm,\
    ProductCategoryDatatablesBuilder, SampleCaseForm, ProductCategoryAttributeForm, ProductAttributeOptionForm,\
    ProductAttributeOptionFormSet, ProductSkuFormSet, ProductSkuForm, PERM_EDIT_PRODUCT
from apps.product.models import Product, Provider, ProductCategory, SampleCase, ProductCategoryAttribute, \
    ProductAttributeOption, ProductSku

HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class ProductPermissionMixin(PermissionRequiredMixin):
    permission_required = PERM_EDIT_PRODUCT


class ProductListView(NavigationHomeMixin, ModelAwareMixin, DatatablesBuilderMixin, AjaxListView):
    model = Product
    queryset = Product.objects.get_empty_query_set()
    datatables_builder_class = ProductDatatablesBuilder
    template_name = 'product/admin/product.list.inc.html'


class ProductListDatatablesView(AjaxDatatablesView):
    model = Product
    datatables_builder_class = ProductListView.datatables_builder_class
    queryset = Product.active_objects.select_related().order_by('-updated')


class ProductCreateView(RequestAwareMixin, ModelAwareMixin, ProductPermissionMixin, AjaxCreateView):
    model = Product
    form_class = ProductForm
    form_action_url_name = 'admin:product:product_create'
    template_name = 'product/admin/product.form.inc.html'


class ProductEditView(ModelAwareMixin, ProductPermissionMixin, AjaxUpdateView):
    model = Product
    form_class = ProductForm
    form_action_url_name = 'admin:product:product_edit'
    template_name = 'product/admin/product.form.inc.html'

    def get_initial(self):
        initial = super(ProductEditView, self).get_initial()
        if self.object:
            initial["detail_images_html"] = self.object.detail_images_html()
            initial["images_html"] = self.object.images_html()
        return initial


class ProductDeleteView(ProductPermissionMixin, ModelActiveView):
    model = Product

    def update(self, obj):
        if not obj.is_deletable():
            return u'存在与属性或SKU的关联，无法删除。'
        super(ProductDeleteView, self).update(obj)


class ProductUpdateView(ProductPermissionMixin, AjaxSimpleUpdateView):
    model = Product

    def update(self, obj):
        action_method = self.kwargs['action_method']
        msg = getattr(self, action_method)(obj)
        if msg:
            return msg
        obj.save()

    def publish(self, product):
        product.is_published = True

    def cancel(self, product):
        product.is_published = False


class ProductSamplecasesEditView(ProductPermissionMixin, AjaxFormsetEditView):
    formset_class = inlineformset_factory(Product, SampleCase, form=SampleCaseForm,
                                          extra=1, max_num=1, can_order=True, can_delete=True)
    parent_model = Product
    model = SampleCase
    form_action_url_name = "admin:product:product_samplecases_edit"
    parent_list_url_name = "admin:product:product_list"


class ProductAttributeOptionsEditView(ProductPermissionMixin, AjaxFormsetEditView):
    formset_class = inlineformset_factory(Product, ProductAttributeOption, form=ProductAttributeOptionForm,
                                          formset=ProductAttributeOptionFormSet,
                                          extra=1, max_num=1, can_order=True, can_delete=True)
    parent_model = Product
    model = ProductAttributeOption
    form_action_url_name = "admin:product:product_attribute_options_edit"
    parent_list_url_name = "admin:product:product_list"
    form_column_count = 4


class ProviderListView(NavigationHomeMixin, ModelAwareMixin, DatatablesBuilderMixin, AjaxListView):
    model = Provider
    queryset = Provider.objects.get_empty_query_set()
    datatables_builder_class = ProviderDatatablesBuilder


class ProviderListDatatablesView(AjaxDatatablesView):
    model = Provider
    datatables_builder_class = ProviderListView.datatables_builder_class
    queryset = Provider.active_objects.select_related().order_by('-updated')


class ProviderCreateView(RequestAwareMixin, ModelAwareMixin, ProductPermissionMixin, AjaxCreateView):
    model = Provider
    form_class = ProviderForm
    form_action_url_name = 'admin:product:provider_create'


class ProviderEditView(ModelAwareMixin,ProductPermissionMixin,  AjaxUpdateView):
    model = Provider
    form_class = ProviderForm
    form_action_url_name = 'admin:product:provider_edit'


class ProviderDeleteView(ProductPermissionMixin, ModelActiveView):
    model = Provider

    def update(self, provider):
        if not provider.is_deletable():
            return u'供应商%s有关联的商品, 不允许删除。' % unicode(self.model)
        super(ProviderDeleteView, self).update(provider)


class ProductCategoryListView(NavigationHomeMixin, ModelAwareMixin, DatatablesBuilderMixin, AjaxListView):
    model = ProductCategory
    queryset = ProductCategory.objects.get_empty_query_set()
    datatables_builder_class = ProductCategoryDatatablesBuilder


class ProductCategoryListDatatablesView(AjaxDatatablesView):
    model = ProductCategory
    datatables_builder_class = ProductCategoryListView.datatables_builder_class
    queryset = ProductCategory.objects.select_related().order_by('name')


class ProductCategoryCreateView(RequestAwareMixin, ModelAwareMixin, ProductPermissionMixin, AjaxCreateView):
    model = ProductCategory
    form_class = ProductCategoryForm
    form_action_url_name = 'admin:product:productcategory_create'


class ProductCategoryEditView(ModelAwareMixin, ProductPermissionMixin, AjaxUpdateView):
    model = ProductCategory
    form_class = ProductCategoryForm
    form_action_url_name = 'admin:product:productcategory_edit'


class ProductCategoryDeleteView(ProductPermissionMixin, AjaxSimpleUpdateView):
    model = ProductCategory

    def update(self, category):
        if category.active_attributes().count() > 0:
            return u'类别%s有关联的属性, 不允许删除' % unicode(self.model)
        category.delete()


class ProductCategoryAttributesEditView(ProductPermissionMixin, AjaxFormsetEditView):
    # NOTE: don't support order the attribute, because we extremely depends on the order of attribute in
    # subsequent sku. see the model definition of "ProductSku"
    formset_class = inlineformset_factory(ProductCategory, ProductCategoryAttribute, form=ProductCategoryAttributeForm,
                                          extra=1, max_num=1, can_order=False, can_delete=False)
    parent_model = ProductCategory
    model = ProductCategoryAttribute
    form_action_url_name = "admin:product:productcategory_attributes_edit"
    parent_list_url_name = "admin:product:productcategory_list"
    form_column_count = 6


class ProductSkuEditView(ProductPermissionMixin, AjaxFormsetEditView):
    formset_class = inlineformset_factory(Product, ProductSku, form=ProductSkuForm,
                                          formset=ProductSkuFormSet,
                                          extra=1, max_num=1, can_order=False, can_delete=False)
    parent_model = Product
    model = ProductSku
    form_action_url_name = "admin:product:product_sku_edit"
    parent_list_url_name = "admin:product:product_list"
    form_column_count = 4
