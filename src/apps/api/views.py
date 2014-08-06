#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import os

from django.views.generic import View


logger = logging.getLogger('apps.'+os.path.basename(os.path.dirname(__file__)))


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


