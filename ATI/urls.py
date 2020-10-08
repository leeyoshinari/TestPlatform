#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

from django.urls import path
from .views import *


# 接口自动化的url
app_name = 'ATI'
urlpatterns = [
    path('run', run, name='run'),
    path('home', home, name='home'),
    path('project', project, name='project'),
    path('project/add', add_project, name='add_project'),
    path('project/update', update_project, name='update_project'),
    path('project/delete', delete_project, name='del_project'),
    path('project/manager', manager_project, name='manager_project'),
    path('interface', interfaces, name='interface'),
    path('interface/add', add_interface, name='add_interface'),
    path('interface/edit', edit_interface, name='edit_interface'),
    path('interface/delete', delete_interface, name='delete_interface'),
    path('scene', scenes, name='scenes'),
    path('scene/add', add_scene, name='add_scene'),
    path('scene/edit', edit_scene, name='edit_scene'),
    path('scene/delete', delete_scene, name='delete_scene'),
    path('scene/interface', show_scene_interface, name='show_scene_interface'),
    path('scene/interface/add', add_scene_interface, name='add_scene_interface'),
    path('scene/interface/move', move_up_or_down, name='move_up_or_down'),
    path('scene/interface/add/interface', add_interface_to_scene, name='add_interface_to_scene'),
    path('scene/isRun', set_is_run, name='set_is_run'),
    path('scene/delete/interface', delete_interface_from_scene, name='delete_interface_from_scene'),
    # path('scene/edit/interface', edit_interface_from_scene, name='edit_interface_from_case'),
    path('plan', plans, name='plans'),
    path('plan/add', add_plan, name='add_plan'),
    path('plan/edit', edit_plan, name='edit_plan'),
    path('plan/copy', copy_plan, name='copy_plan'),
    path('plan/delete', delete_plan, name='delete_plan'),
    path('plan/variable', variables, name='variables'),
    path('plan/variable/add', add_variable, name='add_variable'),
    path('plan/variable/edit', edit_variable, name='edit_variable'),
    path('plan/variable/delete', delete_variable, name='delete_variable'),
    path('plan/scene', show_plan_and_scene, name='show_plan_and_scene'),
    path('plan/scene/add', add_plan_and_scene, name='add_plan_and_scene'),
    path('plan/scene/delete', delete_scene_from_plan, name='delete_scene_from_plan'),
    path('plan/scene/add/scene', add_scene_to_plan, name='add_scene_to_plan'),
    path('plan/scene/isRun', set_is_run_scene, name='set_is_run_scene'),
    path('plan/scene/move', move_up_or_down_scene, name='move_up_or_down_scene'),
    path('plan/scene/edit', edit_scene_from_plan, name='edit_scene_from_plan'),
    path('result', show_result, name='show_result'),
]