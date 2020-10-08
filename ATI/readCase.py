#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

from ATI.models import Variables, Interfaces, Scenes, InterfaceScene, Plans, ScenePlan


def read_scene(plan_id):
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
                'assert_result': case_info.assert_result,
            }
            yield data


def read_variable(plan_id):
    global_variable = {}
    variables = Variables.objects.filter(plan_id=plan_id)
    for V in variables:
        global_variable.update({V.name: V.value})
    return global_variable


def read_setting(plan_id):
    plan = Plans.objects.get(id=plan_id)
    setting = {
        'timing': plan.timing,
        'time_set': plan.time_set,
        'is_email': plan.is_email,
        'email': plan.email,
    }

    return setting

