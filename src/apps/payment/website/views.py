#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from apps.common.website.views import LoginRequiredMixin
from apps.order.models import Order
from django.views.generic.base import TemplateResponseMixin
from django.views.generic import View, ListView
import os


HERE = os.path.dirname(__file__)
logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(HERE)) + '.' + os.path.basename(HERE))


class PaymentFeedbackView(LoginRequiredMixin, TemplateResponseMixin, View):
    template_name = 'payment/website/payment.feedback.html'

    def get(self, request, *args, **kwargs):
        # TODO add some context
        context = {}
        return self.render_to_response(context)