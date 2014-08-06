#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import json
import logging
import os

from django.conf import settings
from django.db.models import Q
from django.shortcuts import render_to_response
from django.utils.decorators import method_decorator
from django.utils.safestring import SafeString
from django.views.decorators.csrf import csrf_exempt
from django.http import (HttpResponse, HttpResponseForbidden)
from django.views.generic import View, DetailView, ListView

from apps.product.models import Product
from apps.wechat.forms import WeChatAccountBindForm
from apps.wechat.handlers import RequestDispatcher, ProductSearchRequestHandler
from apps.wechat.models import WeChatUser
from apps.wechat.protocols import WeChatResponse
from apps.wechat.user_auth import WeChatUserAuth


logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


class CsrfExemptMixin(object):
    """
    Exempts the view from CSRF requirements.

        NOTE: This should be the left-most mixin of a view.
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CsrfExemptMixin, self).dispatch(*args, **kwargs)


class WechatView(CsrfExemptMixin, View):
    def get(self, request, *args, **kwargs):
        # TODO: implement
        pass

    def post(self, request, *args, **kwargs):
        #TODO: implement
        pass


class WeChatResponseMixin:
    content_type = 'application/xml; charset=utf-8'

    def render_to_response(self, response):
        if not response:
            # 返回OK表示收到了消息
            return HttpResponse('OK')
        elif isinstance(response, HttpResponse):
            return response
        elif isinstance(response, WeChatResponse):
            return HttpResponse(response.to_xml(),
                                content_type=self.content_type)
        else:
            assert ('To be impplmented' == None)


class WeChatApiView(WeChatResponseMixin, CsrfExemptMixin, View):
    def get(self, request, *args, **kwargs):

        if self._verify_request(request):
            return HttpResponse(request.GET['echostr'])

        return HttpResponseForbidden()

    def post(self, request, *args, **kwargs):
        """
        curl -v http://localhost:8002/wechat/api \
            -H 'Accept: application/xml'    \
            -H 'Content-Type: application/xml'  \
            -d '<xml>
            <ToUserName><![CDATA[toUser]]></ToUserName>
            <FromUserName><![CDATA[fromUser]]></FromUserName>
            <CreateTime>1348831860</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[What is WIFI password ?]]></Content>
            <MsgId>1234567890123456</MsgId>
            </xml>'
        """
        if not self._verify_request(request):
            return HttpResponseForbidden()

        response = RequestDispatcher.process(request.body)
        if response:
            return self.render_to_response(response)

        return HttpResponseForbidden()

    def _verify_request(self, request):
        """
        网址接入

        公众平台用户提交信息后，微信服务器将发送GET请求到填写的URL上，并且带上四个参数：

        参数	描述
        signature	 微信加密签名
        timestamp	 时间戳
        nonce	     随机数
        echostr	     随机字符串

        开发者通过检验signature对请求进行校验（下面有校验方式）。
        若确认此次GET请求来自微信服务器，请原样返回echostr参数内容，则接入生效，否则接入失败。

        signature结合了开发者填写的token参数和请求中的timestamp参数、nonce参数。

        加密/校验流程：
        1. 将token、timestamp、nonce三个参数进行字典序排序
        2. 将三个参数字符串拼接成一个字符串进行sha1加密
        3. 开发者获得加密后的字符串可与signature对比，标识该请求来源于微信

        curl -v 'http://localhost:8002/wechat/api?signature=abc&timestamp=1234&nonce=xyz123&echostr=hello'
        """
        signature = request.GET['signature']
        timestamp = request.GET['timestamp']
        nonce = request.GET['nonce']

        token = settings.WECHAT_TOKEN

        s = [token, timestamp, nonce]
        s.sort()
        s = ''.join(s)
        expected_signature = hashlib.sha1(s).hexdigest()

        return signature == expected_signature


class WeChatBindView(CsrfExemptMixin, View):
    """
    绑定用户处理
    """

    def get(self, request, *args, **kwargs):
        openid = ""
        if "code" in request.GET:
            code = request.GET["code"]
            access_token, open_id, error_info = WeChatUserAuth.get_access_token_and_openid_with_code(
                code=code,
                app_id=settings.WECHAT_APPID,
                app_secret=settings.WECHAT_SECRET)
            openid = open_id

        if settings.DEBUG:
            if "openid" in request.GET:
                openid = request.GET["openid"]
                try:
                    wechat_user = WeChatUser.objects.get(openid=openid)
                    message = u'微信帐号已经绑定过用户：【{customer_name}】'.format(customer_name=wechat_user.customer.user.name)
                    return HttpResponse(message)
                except WeChatUser.DoesNotExist:
                    pass
        if not openid:
            return HttpResponse(u"服务器无法获取微信帐号信息，暂时无法绑定，请稍后再试")
        wechat_user_bind_form = WeChatAccountBindForm(initial={'openid': openid})
        return render_to_response("wechat/user_bind.html", {"form": wechat_user_bind_form,
                                                            "hide_option_menu": True,
                                                            "hide_toolbar_bar": True})

    def post(self, request, *args, **kwargs):
        wechat_user_bind_form = WeChatAccountBindForm(request.POST)
        if wechat_user_bind_form.is_valid():
            wechat_user_bind_form.save()
            if wechat_user_bind_form.is_pre_wechat_user_exist:
                return HttpResponse(u"绑定成功,请注意帐号安全")
            else:
                return HttpResponse(u"绑定成功")
        else:
            return render_to_response("wechat/user_bind.html", {"form": wechat_user_bind_form,
                                                                "hide_option_menu": True,
                                                                "hide_toolbar_bar": True})


class WeChatProductDetailView(DetailView):
    model = Product
    template_name = 'wechat/product.detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.active_objects.select_related("category", "provider"). \
            prefetch_related("attribute_options__attribute", 'detail_images__image', 'images__image', 'samplecases')

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        return self.get_queryset().get(pk=pk, is_published=True)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(WeChatProductDetailView, self).get_context_data(**kwargs)  # Add in a QuerySet of all the books
        attribute_options, skus = self.object.get_options_and_skus()
        context['attribute_options'] = attribute_options
        context['skus_json'] = SafeString(json.dumps(skus))

        return context


class WeChatProductList(View):
    def get(self, request, *args, **kwargs):
        queryset = Product.active_objects.order_by('-rating', '-updated').filter(is_published=True)
        products = queryset[ProductSearchRequestHandler.max_display_count - 1:]
        return render_to_response("wechat/product.list.html", {'products': products})


class WeChatProductSearch(View):
    def get(self, request, *args, **kwargs):
        keyword = request.GET['q']
        queryset = Product.active_objects.order_by('-rating', '-updated').filter(is_published=True)
        queryset = queryset.filter(Q(name__contains=keyword) | Q(summary__contains=keyword))
        products = queryset[ProductSearchRequestHandler.max_display_count - 1:]
        return render_to_response('wechat/product.search.html', {'products': products})

