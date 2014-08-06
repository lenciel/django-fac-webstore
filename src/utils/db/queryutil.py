#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db.models.manager import Manager
from django.db.models.query import QuerySet
from django.utils import simplejson
from django.core import serializers

def _get_queryset(klass):
    """
    Returns a QuerySet from a Model, Manager, or QuerySet. Created to make
    get_object_or_none more DRY.
    """
    if isinstance(klass, QuerySet):
        return klass
    elif isinstance(klass, Manager):
        manager = klass
    else:
        manager = klass._default_manager
    return manager.all()

def get_object_or_none(klass, *args, **kwargs):
    """
    Uses get() to return an object, or return None if the object does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Note: Like with get(), an MultipleObjectsReturned will be raised if more than one
    object is found.

    Example:

    user = get_object_or_none(get_user_model(), username='admin')
    if user:
        # get user success

    """
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        # 'No %s matches the given query.' % queryset.model._meta.object_name
        return None

def queryset_to_json(queryset):
    """
    把queryset转换为json格式，转换后的结果为一个json数组。

    用途：当AJAX请求需要返回JSON格式的响应的时候，调用这个函数先把queryset转化为JSON格式然后在返回给客户端。

    示例：

    """
    json_string = serializers.serialize('json', queryset, ensure_ascii=False);
    json = simplejson.loads(json_string)
    return json

