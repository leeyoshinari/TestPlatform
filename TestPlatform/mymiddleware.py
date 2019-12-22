#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari
import re
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from .settings import EXCLUDE_URL


exclude_path = [re.compile(item) for item in EXCLUDE_URL]


class AccessAuthMiddleWare(MiddlewareMixin):
    """
    登陆验证
    """
    def process_request(self, request):
        url_path = request.path
        for each in exclude_path:
            if re.match(each, url_path):
                return None

        user = request.COOKIES.get('user')
        password = request.COOKIES.get('password')
        if (user, password) in USERS:
            return None
        else:
            return redirect('/login')
