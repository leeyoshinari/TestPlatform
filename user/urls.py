#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

from django.urls import path
from .views import *

app_name = 'user'
urlpatterns = [
    path('login/', login, name='login'),
    # path('sign/', sign, name='sign'),
    path('logout/', logout, name='logout'),
    path('changePwd/', changePwd, name='changePwd'),
    path('userInfo/', userInfo, name='userInfo'),
    path('tester/', home, name='home'),
]
