#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

from django.template import Library
register = Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(str(key), None)
