#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
import os
from apps.common import exceptions

HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class LoginRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            # 不允许管理员访问需要授权的前端页面
            if not request.user.customer:
                logger.info(u"A staff attempt to go %s which is intend for customer " % request.get_full_path())
                return HttpResponseRedirect(reverse("website:home"))
        else:
            if request.method == 'GET':
                login_url = reverse("website:login") + "?next=" + request.get_full_path()
            else:
                raise exceptions.AjaxAuthRequired()
            return HttpResponseRedirect(login_url)

        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class StaffRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated() and request.user.is_staff:
            return super(StaffRequiredMixin, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied()