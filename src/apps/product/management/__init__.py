#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob
import logging
import shutil
from django.conf import settings
from django.db.models.signals import post_syncdb
import os
import apps.product.models

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


def deploy_test_stuff(sender, **kwargs):
    """
    deploy a couple of test image to folder "image"
    """
    fixtures_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fixtures')
    # the images are built from http://dummyimage.com/
    images = glob.glob(fixtures_path+"/*.png")
    for image in images:
        try:
            shutil.copy(image, os.path.join(settings.MEDIA_ROOT, settings.MEDIA_IMAGE_PREFIX))
        except:
            pass

    htmls = glob.glob(fixtures_path+"/*.html")
    for html in htmls:
        try:
            shutil.copy(html, os.path.join(settings.MEDIA_ROOT, settings.MEDIA_CONTENT_PREFIX))
        except:
            pass

post_syncdb.connect(deploy_test_stuff, sender=apps.product.models)