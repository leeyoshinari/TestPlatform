#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

from django.urls import path
from .views import *

urlpatterns = [
	path('login/', login, name='login'),
	path('signin/', signin, name='signin'),
	path('log_in/', log_in, name='log_in'),
	path('sign_in/', sign_in, name='sign_in'),
	path('logout/', logout, name='logout'),
	path('project/', home, name='home'),
]