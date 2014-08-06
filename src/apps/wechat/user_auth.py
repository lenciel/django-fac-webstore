# -*- coding: utf-8 -*-
__author__ = 'zhangbo'

import urllib
import urllib2
import json


class WeChatErrorCode(object):
    """
    微信错误码
    """
    ERROR_UNDEFINED = -2
    ERROR_SUCCEED = 0

    def __init__(self, json_data=None):
        """
        {"errcode":40013,"errmsg":"invalid appid"}
        """
        self.error_code = 0
        self.error_message = ""
        self.parse_from_json_data(json_data)

    def parse_from_json_data(self, json_data):
        """
        从 json_data 解析数据
        """
        if json_data and isinstance(json_data, dict):
            if "errcode" in json_data and "errmsg" in json_data:
                self.error_code = int(json_data["errcode"])
                self.error_message = json_data["errmsg"]

    def is_error(self):
        """
        是否是错误
        """
        return WeChatErrorCode.ERROR_SUCCEED != self.error_code

    @staticmethod
    def get_undefined_error(error_message=u"未知错误"):
        """
        返回未知错误
        """
        error_info = WeChatErrorCode()
        error_info.error_code = WeChatErrorCode.ERROR_UNDEFINED
        error_info.error_message = error_message
        return error_info


class WeChatUserAuth(object):
    """
    微信授权
    """
    AUTH_CODE_TYPE_BASE = "snsapi_base"
    AUTH_CODE_TYPE_USER_INFO = "snsapi_userinfo"
    AUTH_CODE_API = "https://open.weixin.qq.com/connect/oauth2/authorize"
    AUTH_ACCESS_TOKEN_API = "https://api.weixin.qq.com/sns/oauth2/access_token"
    AUTH_REFRESH_TOKEN_API = "https://api.weixin.qq.com/sns/oauth2/refresh_token"
    AUTH_GET_USER_INFO_API = "https://api.weixin.qq.com/sns/userinfo"

    @staticmethod
    def auth_request(url_api, params=None,
                     post_data=None,
                     encoding='utf-8'):
        """
        向微信服务器发起请求
        """
        if params:
            if isinstance(params, dict):
                for key in params:
                    value = params[key]
                    if isinstance(value, unicode):
                        params[key] = value.encode(encoding=encoding)
                params = urllib.urlencode(params)
            elif isinstance(params, (str, unicode)):
                if isinstance(params, unicode):
                    params = params.encode(encoding=encoding)
                params = urllib.quote(params)

        if post_data and isinstance(post_data, unicode):
            post_data = post_data.encode(encoding=encoding)

        if params:
            request_url = "{api}?{params}".format(api=url_api, params=params)
        else:
            request_url = url_api
        response = urllib2.urlopen(request_url, data=post_data)
        json_data = response.read()
        json_data = json.loads(json_data)
        error_info = WeChatErrorCode(json_data)
        return json_data, error_info

    @staticmethod
    def get_auth_code_api(redirect_uri, params, app_id,
                          scope_type=AUTH_CODE_TYPE_USER_INFO,
                          wechat_redirect=True):
        """
        第一步：用户同意授权，获取code

        在确保微信公众账号拥有授权作用域（scope参数）的权限的前提下（服务号获得高级接口后，
        默认带有scope参数中的snsapi_base和snsapi_userinfo），引导关注者打开如下页面：

        https://open.weixin.qq.com/connect/oauth2/authorize?
        appid=APPID&redirect_uri=REDIRECT_URI&response_type=code&scope=SCOPE&state=STATE#wechat_redirect
        若提示“该链接无法访问”，请检查参数是否填写错误，是否拥有scope参数对应的授权作用域权限。

        参数说明

        参数	是否必须	说明
        appid	 是	 公众号的唯一标识
        redirect_uri	 是	 授权后重定向的回调链接地址
        response_type	 是	 返回类型，请填写code
        scope	 是	 应用授权作用域，snsapi_base （不弹出授权页面，直接跳转，只能获取用户openid），
                snsapi_userinfo （弹出授权页面，可通过openid拿到昵称、性别、所在地。并且，即使在未关注的情况下，只要用户授权，也能获取其信息）
        state	 否	 重定向后会带上state参数，开发者可以填写任意参数值
        #wechat_redirect	 否	 直接在微信打开链接，可以不填此参数。做页面302重定向时候，必须带此参数

        """
        if not params:
            params = "state"
        elif isinstance(params, unicode):
            params = params.encode("utf-8")

        auth_code_api_params = {"appid": app_id,
                                "redirect_uri": redirect_uri,
                                "response_type": "code",
                                "scope": scope_type,
                                "state": params
        }
        auth_code_api_params = urllib.urlencode(auth_code_api_params)
        auth_code_api = "{api}?{params}".format(api=WeChatUserAuth.AUTH_CODE_API, params=auth_code_api_params)
        if wechat_redirect:
            auth_code_api += "#wechat_redirect"
        return auth_code_api

    @staticmethod
    def get_access_token_and_openid_with_code(code, app_id, app_secret):
        """
        通过code换取网页授权access_token

        首先请注意，这里通过code换取的网页授权access_token,与基础支持中的access_token不同。
        公众号可通过下述接口来获取网页授权access_token。如果网页授权的作用域为snsapi_base，
        则本步骤中获取到网页授权access_token的同时，也获取到了openid，snsapi_base式的网页授权流程即到此为止。

        请求方法

        获取code后，请求以下链接获取access_token：
        https://api.weixin.qq.com/sns/oauth2/access_token?appid=APPID&secret=SECRET&code=CODE&grant_type=authorization_code
        参数说明

        参数	是否必须	说明
        appid	 是	 公众号的唯一标识
        secret	 是	 公众号的appsecret
        code	 是	 填写第一步获取的code参数
        grant_type	 是	 填写为authorization_code
        返回说明

        正确时返回的JSON数据包如下：

        {
           "access_token":"ACCESS_TOKEN",
           "expires_in":7200,
           "refresh_token":"REFRESH_TOKEN",
           "openid":"OPENID",
           "scope":"SCOPE"
        }
        参数	描述
        access_token	 网页授权接口调用凭证,注意：此access_token与基础支持的access_token不同
        expires_in	 access_token接口调用凭证超时时间，单位（秒）
        refresh_token	 用户刷新access_token
        openid	 用户唯一标识，请注意，在未关注公众号时，用户访问公众号的网页，也会产生一个用户和公众号唯一的OpenID
        scope	 用户授权的作用域，使用逗号（,）分隔

        错误时微信会返回JSON数据包如下（示例为Code无效错误）:

        {"errcode":40029,"errmsg":"invalid code"}
        """
        params = {"appid": app_id,
                  "secret": app_secret,
                  "code": code,
                  "grant_type": "authorization_code"
        }
        access_token = None
        open_id = None
        try:
            json_data, error_info = WeChatUserAuth.auth_request(url_api=WeChatUserAuth.AUTH_ACCESS_TOKEN_API,
                                                                params=params)
            if "access_token" in json_data:
                access_token = json_data["access_token"]
            if "openid" in json_data:
                open_id = json_data["openid"]
        except:
            access_token = None
            open_id = None
            error_info = WeChatErrorCode.get_undefined_error()
        return access_token, open_id, error_info

    @staticmethod
    def refresh_auth_token_and_openid(app_id, old_token):
        """
        由于access_token拥有较短的有效期，当access_token超时后，可以使用refresh_token进行刷新，
        refresh_token拥有较长的有效期（7天、30天、60天、90天），当refresh_token失效的后，需要用户重新授权。

        请求方法

        获取第二步的refresh_token后，请求以下链接获取access_token：
        https://api.weixin.qq.com/sns/oauth2/refresh_token?appid=APPID&grant_type=refresh_token&refresh_token=REFRESH_TOKEN
        参数	是否必须	说明
        appid	 是	 公众号的唯一标识
        grant_type	 是	 填写为refresh_token
        refresh_token	 是	 填写通过access_token获取到的refresh_token参数
        返回说明

        正确时返回的JSON数据包如下：

        {
           "access_token":"ACCESS_TOKEN",
           "expires_in":7200,
           "refresh_token":"REFRESH_TOKEN",
           "openid":"OPENID",
           "scope":"SCOPE"
        }
        参数	描述
        access_token	 网页授权接口调用凭证,注意：此access_token与基础支持的access_token不同
        expires_in	 access_token接口调用凭证超时时间，单位（秒）
        refresh_token	 用户刷新access_token
        openid	 用户唯一标识
        scope	 用户授权的作用域，使用逗号（,）分隔

        错误时微信会返回JSON数据包如下（示例为Code无效错误）:

        {"errcode":40029,"errmsg":"invalid code"}
        """
        params = {"appid": app_id,
                  "refresh_token": old_token,
                  "grant_type": "refresh_token"
        }
        access_token = None
        open_id = None
        try:
            json_data, error_info = WeChatUserAuth.auth_request(url_api=WeChatUserAuth.AUTH_REFRESH_TOKEN_API,
                                                                params=params)
            if "access_token" in json_data:
                access_token = json_data["access_token"]
            if "openid" in json_data:
                open_id = json_data["openid"]
        except:
            access_token = None
            open_id = None
            error_info = WeChatErrorCode.get_undefined_error()
        return access_token, open_id, error_info

    @staticmethod
    def get_user_info(user_id, access_token, lang="zh_CN"):
        """
        拉取用户信息(需scope为 snsapi_userinfo)

        如果网页授权作用域为snsapi_userinfo，则此时开发者可以通过access_token和openid拉取用户信息了。

        请求方法

        http：GET（请使用https协议）
        https://api.weixin.qq.com/sns/userinfo?access_token=ACCESS_TOKEN&openid=OPENID&lang=zh_CN
        参数说明

        参数	描述
        access_token	 网页授权接口调用凭证,注意：此access_token与基础支持的access_token不同
        openid	 用户的唯一标识
        lang	 返回国家地区语言版本，zh_CN 简体，zh_TW 繁体，en 英语
        返回说明

        正确时返回的JSON数据包如下：

        {
           "openid":" OPENID",
           " nickname": NICKNAME,
           "sex":"1",
           "province":"PROVINCE"
           "city":"CITY",
           "country":"COUNTRY",
            "headimgurl":    "http://wx.qlogo.cn/mmopen/g3MoLrhJbERQQxCfHe/46",
            "privilege":[
            "PRIVILEGE1"
            "PRIVILEGE2"
            ]
        }
        参数	描述
        openid	 用户的唯一标识
        nickname	 用户昵称
        sex	 用户的性别，值为1时是男性，值为2时是女性，值为0时是未知
        province	 用户个人资料填写的省份
        city	 普通用户个人资料填写的城市
        country	 国家，如中国为CN
        headimgurl	 用户头像，最后一个数值代表正方形头像大小（有0、46、64、96、132数值可选，0代表640*640正方形头像），用户没有头像时该项为空
        privilege	 用户特权信息，json 数组，如微信沃卡用户为（chinaunicom）

        错误时微信会返回JSON数据包如下（示例为openid无效）:

        {"errcode":40003,"errmsg":" invalid openid "}

        """
        params = {"access_token": access_token, "openid": user_id, "lang": lang}
        try:
            json_data, error_info = WeChatUserAuth.auth_request(url_api=WeChatUserAuth.AUTH_GET_USER_INFO_API,
                                                                params=params)
        except:
            json_data = None
            error_info = WeChatErrorCode.get_undefined_error()
        return json_data, error_info
