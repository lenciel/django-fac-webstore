#!/usr/bin/env python
# -*- coding: utf-8 -*-


def get_field_max_length(model, field_name):
    return model._meta.get_field(field_name).max_length
