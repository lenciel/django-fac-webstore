#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.views.generic import DetailView
from apps.cms.models import Article
from apps.common.website.views import StaffRequiredMixin


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'cms/website/article.detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        return Article.active_objects

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        return self.get_queryset().get(pk=pk, is_published=True)


class ArticlePreviewView(StaffRequiredMixin, ArticleDetailView):

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        return self.get_queryset().get(pk=pk)

    def get_context_data(self, **kwargs):
        context = super(ArticlePreviewView, self).get_context_data(**kwargs)
        context['is_preview'] = True
        return context