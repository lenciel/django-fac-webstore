#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from apps.foundation.forms import ImageForm

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


IMAGE_MIN_WIDTH = 0
IMAGE_MIN_HEIGHT = 0

@csrf_exempt
def upload_image_view(request):
    form = ImageForm(request.POST, request.FILES)
    status = 400
    if form.is_valid():
        obj = form.save(commit=False)
        if obj.width < IMAGE_MIN_WIDTH or obj.height < IMAGE_MIN_HEIGHT:
            state = u'图片尺寸至少%dx%d' % (IMAGE_MIN_WIDTH, IMAGE_MIN_HEIGHT)
        else:
            state = 'SUCCESS'
            obj.save()
        status = 200
        resp = "{'original':'%s','url':'%s','title':'%s','state':'%s'}" % \
               ("", obj.image_file.url, "", state)
        return HttpResponse(content=resp, status=status)

    return HttpResponse(status=status)
