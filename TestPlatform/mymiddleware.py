#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari
import re
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from .settings import EXCLUDE_URL


class AccessAuthMiddleWare(MiddlewareMixin):
    """
    登陆验证
    """
    def process_request(self, request):
        if re.search(EXCLUDE_URL, request.path):
            return None

        if request.user.is_authenticated:
            return None
        else:
            return redirect('/login')
