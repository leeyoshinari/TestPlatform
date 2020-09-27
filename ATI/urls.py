#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

from django.urls import path
from .views import *


# 接口自动化的url
app_name = 'ATI'
urlpatterns = [
    path('home', home, name='home'),
    path('project', project, name='project'),
    path('project/add', add_project, name='add_project'),
    path('project/update', update_project, name='update_project'),
    path('project/delete', del_project, name='del_project'),
    path('project/manager', manager_project, name='manager_project'),
    path('variable', variables, name='variables'),
    path('variable/add', add_variable, name='add_variable'),
    path('variable/delete', delete_variable, name='delete_variable'),
    path('variable/edit', edit_variable, name='edit_variable'),
    path('interface', interfaces, name='interface'),
    path('interface/add', add_interface, name='add_interface'),
    path('interface/edit', edit_interface, name='edit_interface'),
    path('interface/delete', delete_interface, name='delete_interface'),
    path('case', cases, name='cases'),
    path('case/add', add_case, name='add_case'),
    path('case/edit', edit_case, name='edit_case'),
    path('case/delete', delete_case, name='delete_case'),
    path('case/interface', show_case_interface, name='show_case_interface'),
    path('case/interface/add', add_case_interface, name='add_case_interface'),
    path('case/interface/move', move_up_or_down, name='move_up_or_down'),
    path('case/interface/add/interface', add_interface_to_case, name='add_interface_to_case'),
    path('case/case/isRun', set_is_run, name='set_is_run'),
    path('case/delete/interface', delete_interface_from_case, name='delete_interface_from_case'),
    path('case/edit/interface', edit_interface_from_case, name='edit_interface_from_case'),
    path('plan', plans, name='plans'),
    path('plan/add', add_plan, name='add_plan'),
]