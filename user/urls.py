#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

from django.urls import path
from .views import *

urlpatterns = [
	path('login/', login, name='login'),
	path('sign/', sign, name='sign'),
	path('logout/', logout, name='logout'),
	path('tester/', home, name='home'),
]