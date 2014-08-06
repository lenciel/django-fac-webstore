#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from django import forms
from .models import Image

logger = logging.getLogger('apps.' + os.path.basename(os.path.dirname(__file__)))


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = {"image_file"}

