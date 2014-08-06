#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import uuid
from django.utils import timezone


def gen_random_string(size=7):
    """
    产生随机的字符串。

    参数
    size: 目标随机字符串的长度，默认7。 62^7 = 3521614606208 足够大。

    该算法虽然简单，但产生的key足够随机，
    在MAC OSX上的测试结果显示100万个key可能有一个冲突的。
    """
    keys = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    keys_len = 62
    key = ''
    for random in os.urandom(size):
        key += keys[ord(random) % keys_len]
    return key


def gen_uuid_filename(suffix_name):
    """
    使用UUID算法产生文件名称
    """
    return "%s.%s" % (str(uuid.uuid4()).replace('-', ''), suffix_name)


def gen_timestamp_filename(suffix_name):
    return "%s.%s" % (timezone.now().strftime("%Y%m%d%H%M%S"), suffix_name)