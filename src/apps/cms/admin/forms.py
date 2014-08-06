#!/usr/bin/env python
# -*- coding: utf-8 -*-
import StringIO
import logging
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
import os
from django import forms
from apps.cms.models import Article
from apps.common.ace import AceClearableFileInput
from apps.common.admin.datatables import DatatablesIdColumn, DatatablesBuilder, DatatablesImageColumn, DatatablesTextColumn,\
    DatatablesBooleanColumn, DatatablesUserChoiceColumn, DatatablesDateTimeColumn, DatatablesColumnActionsRender,\
    DatatablesActionsColumn
from apps.product.models import Product

HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class ArticleForm(forms.ModelForm):
    content_html = forms.CharField(label=u'内容',
                                   widget=forms.Textarea())

    products = forms.ModelMultipleChoiceField(label=u'产品',
                                              required=False,
                                              queryset=Product.active_objects.only('name').all())

    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = "required input-xxlarge limited"
        self.fields['summary'].widget.attrs['class'] = "limited col-md-10"
        self.fields['source'].widget.attrs['class'] = "limited col-md-10"
        self.fields['products'].widget.attrs['class'] = "col-md-10"
        self.fields['products'].widget.attrs['data-placeholder'] = "选择关联产品"

    class Meta:
        model = Article
        fields = (
            'title', 'title_image_file', 'products', 'summary', 'source', 'content_html')

        widgets = {
            # use FileInput widget to avoid show clearable link and text
            'title_image_file': AceClearableFileInput(),
        }

    def clean(self):
        cleaned_data = super(ArticleForm, self).clean()
        # keep the old image and delete it if changed at save()
        self.old_title_image_file = self.instance.title_image_file
        return cleaned_data

    def save(self, commit=False):
        article = super(ArticleForm, self).save(commit)
        #mock a html file to feed to article.content_file
        if article.content_file:
            # update it if has content file
            with open(article.content_file.path, 'w') as f:
                f.write(self.cleaned_data['content_html'].encode('utf-8'))
        else:
            buf = StringIO.StringIO(self.cleaned_data['content_html'].encode('utf-8'))
            article.content_file = SimpleUploadedFile("content.html", buf.read())

        if not hasattr(article, "creator"):
            article.creator = self.initial['request'].user
        article.save()
        article.products.clear()
        for product in self.cleaned_data['products']:
            product.article = article
            product.save(update_fields=["article"])
        # return id to avoid caller to model.save() again
        return article


class ArticleDatatablesBuilder(DatatablesBuilder):

    id = DatatablesIdColumn()

    title = DatatablesTextColumn(label='标题',
                                 is_searchable=True,
                                 render=(lambda request, model, field_name:
                                         u"<a href='%s' target='_blank'>%s</a>" % (model.content_url(), model.title)))


    title_image_file = DatatablesImageColumn(label='标题图片')

    summary = DatatablesTextColumn(label='摘要',
                                   is_searchable=True)

    products = DatatablesTextColumn(label='产品',
                                    render=(lambda request, model, field_name:
                                            u"<ul>" + "".join([u"<li>%s</li>" % x.name for x in model.products.all()]) + u"</ul>"))

    is_published = DatatablesBooleanColumn((('', u'全部'), (1, u'发布'), (0, u'草稿')),
                                           label='状态',
                                           is_searchable=True,
                                           col_width='7%',
                                           render=(lambda request, model, field_name:
                                                   u'<span class="label label-info"> 发布 </span>' if model.is_published else
                                                   u'<span class="label label-warning"> 草稿 </span>'))

    creator = DatatablesUserChoiceColumn(label='作者',)

    updated = DatatablesDateTimeColumn(label='修改时间')

    def actions_render(request, model, field_name):
        if model.is_published:
            actions = [{'is_link': False, 'css_class': 'btn-yellow', 'name': 'cancel', 'text': u'撤销', 'icon': 'icon-cut'}]
        else:
            actions = [{'is_link': True, 'css_class': 'btn-info', 'name': 'edit', 'text': u'编辑', 'icon': 'icon-edit'},
                       {'is_link': False, 'css_class': 'btn-warning', 'name': 'publish', 'text': u'发布', 'icon': 'icon-save'}]
        actions.append({'is_link': False, 'css_class': 'btn-warning', 'name': 'delete', 'text': u'删除', 'icon': 'icon-remove'})
        actions.append({'is_link': False, 'name': 'preview', 'text': u'预览', 'icon': 'icon-eye-open', 'handler_type': 'customize',
                        'url': reverse('website:cms:article_preview', kwargs={'pk': model.id}) })
        return DatatablesColumnActionsRender(actions=actions).render(request, model, field_name)

    _actions = DatatablesActionsColumn(render=actions_render)
