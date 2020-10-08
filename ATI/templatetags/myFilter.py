#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

from django.template import Library
register = Library()


@register.filter
def calc_radio(v1, v2):
    if v2:
        return round((v1 / v2) * 100, 2)
    else:
        return 0


@register.filter
def get_item(dictionary, key):
    return dictionary.get(str(key), None)


@register.filter
def list_index(lists, index):
    return lists[index]


@register.filter
def calc_time(t):
    if t <= 300:
        return f'{t:.2f} s'
    elif t <= 6000:
        return f'{round(t / 60, 2)} min'
    else:
        return f'{round(t / 3600, 2)} h'
