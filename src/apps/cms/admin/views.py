#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView
import os
from apps.cms.models import Article
from apps.common.admin.views import AjaxSimpleUpdateView, ModelAwareMixin, RequestAwareMixin,\
    NavigationHomeMixin, DatatablesBuilderMixin, AjaxListView, AjaxCreateView, AjaxUpdateView, AjaxDatatablesView
from .forms import ArticleForm, ArticleDatatablesBuilder

HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class ArticleListView(NavigationHomeMixin, ModelAwareMixin, DatatablesBuilderMixin, AjaxListView):
    model = Article
    datatables_builder_class = ArticleDatatablesBuilder
    queryset = Article.objects.get_empty_query_set()
    template_name = 'cms/admin/article.list.inc.html'


class ArticleListDatatablesView(AjaxDatatablesView):
    model = Article
    datatables_builder_class = ArticleListView.datatables_builder_class
    queryset = Article.active_objects.prefetch_related("products").select_related().order_by('-updated')


class ArticleCreateView(RequestAwareMixin, ModelAwareMixin, AjaxCreateView):
    model = Article
    form_class = ArticleForm
    form_action_url_name = 'admin:cms:article_create'
    template_name = 'cms/admin/article.form.inc.html'


class ArticleEditView(ModelAwareMixin, AjaxUpdateView):
    model = Article
    form_class = ArticleForm
    form_action_url_name = 'admin:cms:article_edit'
    template_name = 'cms/admin/article.form.inc.html'

    def get_initial(self):
        initial = super(ArticleEditView, self).get_initial()
        if self.object:
            initial["content_html"] = self.object.content_html()
            initial["products"] = self.object.products.all()
        return initial


class ArticleDeleteView(AjaxSimpleUpdateView):
    model = Article

    def update(self, obj):
        obj.is_active = False
        obj.save()


class ArticlePublishView(AjaxSimpleUpdateView):
    model = Article

    def update(self, obj):
        obj.is_published = True
        obj.save()


class ArticleCancelView(AjaxSimpleUpdateView):
    model = Article

    def update(self, obj):
        obj.is_published = False
        obj.save()


class ArticleHtmlRedirectView(RedirectView):
    def get_redirect_url(self, pk):
        article = get_object_or_404(Article, pk=pk)
        return article.content_file.url