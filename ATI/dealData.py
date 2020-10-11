#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import time
from ATI.models import Variables, Interfaces, InterfaceScene, Plans, ScenePlan
from ATI.request import get


def read_scene(plan_id):
    """
    根据测试计划id读取测试场景，再根据场景读取测试用例
    """
    scenes = ScenePlan.objects.filter(plan_id=plan_id, is_run=1).order_by('display_sort')
    for scene in scenes:
        cases = InterfaceScene.objects.filter(scene_id=scene.scene_id, is_run=1).order_by('display_sort')
        for case in cases:
            case_info = Interfaces.objects.get(id=case.interface_id)
            data = {
                'case_id': case_info.interface_id,
                'case_name': case_info.name,
                'url': case_info.interface,
                'protocol': case_info.protocol,
                'method': case_info.method,
                'param': case_info.parameter,
                'timeout': case_info.timeout,
                'header': case_info.header,
                'pre_process': case_info.pre_process,
                'post_process': case_info.post_process,
                'expect_result': case_info.expect_result,
                'assert_method': case_info.assert_method,
                'true_result': case_info.true_result,
            }
            yield data


def read_variable(plan_id):
    """
    读取初始化的全局变量
    """
    global_variable = {}
    variables = Variables.objects.filter(plan_id=plan_id)
    for V in variables:
        global_variable.update({V.name: V.value})
    return global_variable


def read_setting(plan_id):
    """
    读取测试计划设置
    """
    plan = Plans.objects.get(id=plan_id)
    setting = {
        'timing': plan.timing,
        'time_set': plan.time_set,
        'is_email': plan.is_email,
        'email': plan.email,
    }

    return setting


def scan_tasks():
    tasks = Plans.objects.filter(is_running=1)
    for task in tasks:
        if task.timing == 1:
            set_hour = int(task.time_set.split(':')[0])
            set_minute = int(task.time_set.split(':')[1])
            if set_hour == int(time.strftime('%H')) and set_minute == int(time.strftime('%M')):
                res = get(f'http://{task.host}/run?Id={task.plan_id}')
                if res['code'] == 0:
                    task.is_running = 0
                    task.save()
                else:
                    pass
        elif task.timing == 2:
            interval = int(task.time_set)
            if time.time() - task.last_run_time > interval:
                res = get(f'http://{task.host}/ATI/run?Id={task.plan_id}')
                if res['code'] == 0:
                    task.last_run_time = int(time.time())
                    task.save()
                else:
                    pass
        else:
            set_hour = int(task.time_set.split(':')[0])
            set_minute = int(task.time_set.split(':')[1])
            if set_hour == int(time.strftime('%H')) and set_minute == int(time.strftime('%M')):
                res = get(f'http://{task.host}/run?Id={task.plan_id}')

