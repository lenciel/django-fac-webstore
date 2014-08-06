#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views


urlpatterns = patterns('',
    url(r'^list$', views.ProductListView.as_view(), name='product_list'),
    url(r'^list.datatables$', views.ProductListDatatablesView.as_view(), name='product_list.datatables'),
    url(r'^create$', views.ProductCreateView.as_view(), name='product_create'),
    url(r'^(?P<pk>\d+)/edit$', views.ProductEditView.as_view(), name='product_edit'),
    url(r'^(?P<pk>\d+)/delete$', views.ProductDeleteView.as_view(), name='product_delete'),
    url(r'^(?P<pk>\d+)/samplecases/edit$', views.ProductSamplecasesEditView.as_view(), name='product_samplecases_edit'),
    url(r'^(?P<pk>\d+)/attribute/options/edit$', views.ProductAttributeOptionsEditView.as_view(), name='product_attribute_options_edit'),
    url(r'^(?P<pk>\d+)/sku/edit$', views.ProductSkuEditView.as_view(), name='product_sku_edit'),
    url(r'^(?P<pk>\d+)/update/(?P<action_method>\w+)$', views.ProductUpdateView.as_view(), name='product_update'),
)

urlpatterns += patterns('',
    url(r'^provider/list$', views.ProviderListView.as_view(), name='provider_list'),
    url(r'^provider/list.datatables$', views.ProviderListDatatablesView.as_view(), name='provider_list.datatables'),
    url(r'^provider/create$', views.ProviderCreateView.as_view(), name='provider_create'),
    url(r'^provider/(?P<pk>\d+)/edit$', views.ProviderEditView.as_view(), name='provider_edit'),
    url(r'^provider/(?P<pk>\d+)/delete$', views.ProviderDeleteView.as_view(), name='provider_delete'),
)

urlpatterns += patterns('',
    url(r'^category/list$', views.ProductCategoryListView.as_view(), name='productcategory_list'),
    url(r'^category/list.datatables$', views.ProductCategoryListDatatablesView.as_view(), name='productcategory_list.datatables'),
    url(r'^category/create$', views.ProductCategoryCreateView.as_view(), name='productcategory_create'),
    url(r'^category/(?P<pk>\d+)/edit$', views.ProductCategoryEditView.as_view(), name='productcategory_edit'),
    url(r'^category/(?P<pk>\d+)/delete$', views.ProductCategoryDeleteView.as_view(), name='productcategory_delete'),
    url(r'^category/(?P<pk>\d+)/attributes/edit$', views.ProductCategoryAttributesEditView.as_view(), name='productcategory_attributes_edit'),
)
