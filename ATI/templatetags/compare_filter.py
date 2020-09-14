#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

from django.template import Library
register = Library()


@register.filter
def is_equal(v1, v2):
    return str(v1) == str(v2)
