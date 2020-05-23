#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

from django.urls import path
from .views import *


# 接口自动化的url
app_name = 'ATI'
urlpatterns = [
    path('home/', home, name='home'),
    path('project/', project, name='project'),
    path('project/add/', add_project, name='add_project'),
    path('project/update', update_project, name='update_project'),
    path('project/delete/', del_project, name='del_project'),
    path('project/manager/', manager_project, name='manager_project'),
    path('variable/', variables, name='variables'),
]