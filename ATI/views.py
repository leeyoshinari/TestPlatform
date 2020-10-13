#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leeyoshinari

import math
import time
import json
import logging
import traceback
from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.models import User
from django.db.models import Q, Max
from django.http import JsonResponse
from django.db.models.deletion import ProtectedError
from user.models import Projects, UserProject, Results
from ATI.models import Variables, Interfaces, Scenes, InterfaceScene, Plans, ScenePlan
from ATI.scheduler import Schedule
from common.timeFormat import time_strftime


logger = logging.getLogger('django')
schedule = Schedule()


def add_to_task(request):
	"""
	执行测试计划
	"""
	username = request.user.username
	plan_id = request.GET.get('Id')
	is_cancel = request.GET.get('isCancel')
	try:
		if is_cancel:
			r = Plans.objects.get(id=plan_id)
			r.is_running = 0
			r.save()
			logger.info(f'{username}，测试计划取消执行成功，id={plan_id}')
			return JsonResponse({'code': 0, 'msg': '取消执行成功', 'data': plan_id}, json_dumps_params={'ensure_ascii': False})
		else:
			r = Plans.objects.get(id=plan_id)
			if r.timing == 0:
				logger.info(f'{username}，测试计划立即执行，id={plan_id}')
				return JsonResponse({'code': 2, 'msg': '测试计划立即执行', 'data': plan_id}, json_dumps_params={'ensure_ascii':False})
			else:
				r.is_running = 1
				r.save()
				logger.info(f'{username}，测试计划添加成功，id={plan_id}')
				return JsonResponse({'code': 0, 'msg': '测试计划执行成功', 'data': plan_id}, json_dumps_params={'ensure_ascii': False})
	except Exception as err:
		logger.error(err)
		logger.error(traceback.format_exc())
		logger.info(f'{username}，测试计划执行失败，id={plan_id}')
		return JsonResponse({'code': 1, 'msg': '测试计划执行失败', 'data': plan_id}, json_dumps_params={'ensure_ascii': False})


def run(request):
	"""
	执行测试计划
	"""
	try:
		plan_id = request.GET.get('Id')
		r = Plans.objects.get(id=plan_id)
		plan = Results.objects.create(plan_id=plan_id, plan_name=r.name, project_id=r.project_id, status=1, type='ATI')
		schedule.task = (plan.id, plan_id)
		logger.info(f'执行测试计划成功，id={plan_id}')
		return JsonResponse({'code': 0, 'msg': '测试计划执行成功', 'data': None}, json_dumps_params={'ensure_ascii':False})
	except Exception as err:
		logger.error(err)
		logger.error(traceback.format_exc())
		logger.error(f'执行测试计划失败, {request.path}')
		return JsonResponse({'code': 1, 'msg': '测试计划执行失败', 'data': None}, json_dumps_params={'ensure_ascii':False})


def home(request):
	if request.method == 'GET':
		page_num = request.GET.get('pageNum')
		if page_num:
			page_num = int(page_num)
		else:
			page_num = 1

		user_name = request.user.username
		start_index = (page_num - 1) * 15
		end_index = page_num * 15

		all_list = []
		total_num = UserProject.objects.filter(type='ATI', user_name=user_name).count()
		project_ids = UserProject.objects.filter(type='ATI', user_name=user_name).order_by('-create_time')[start_index:end_index].values('project_id')
		for pro_id in project_ids:
			pro_id = pro_id['project_id']
			total_info = {'project_name': Projects.objects.get(id=pro_id).name,
						  'plan_num': Plans.objects.filter(project_id=pro_id).count(),
						  'scene_num': Scenes.objects.filter(project_id=pro_id).count(),
						  'case_num': Interfaces.objects.filter(project_id=pro_id).count(),
						  'times': 0, 'total_case': 0, 'total_success': 0, 'total_interval': 0}

			results = Results.objects.filter(project_id=pro_id)
			for res in results:
				if res.status == 3:
					total_info['total_case'] += res.total_num
					total_info['total_success'] += res.success_num
					total_info['total_interval'] += res.interval
					total_info['times'] += 1

			all_list.append(total_info)

		return render(request, 'ATI/home.html', context={'username': user_name, 'all_list': all_list, 'page_num': page_num, 'total_num': math.ceil(total_num / 15)})


def project(request):
	"""
	查询当前用户下所有的项目
	:param request:
	:return:
	"""
	if request.method == 'GET':
		page_num = request.GET.get('pageNum')
		if page_num:
			page_num = int(page_num)
		else:
			page_num = 1
		user_name = request.user.username
		start_index = (page_num - 1) * 10
		end_index = page_num * 10
		project_ids = UserProject.objects.filter(type='ATI', user_name=user_name).values('project_id')
		total_num = Projects.objects.filter(type='ATI', id__in=project_ids).count()
		projects = Projects.objects.filter(type='ATI', id__in=project_ids).order_by('-update_time')[start_index:end_index]
		return render(request, 'ATI/project/index.html', context={'username': user_name, 'projects': projects, 'page_num': page_num, 'total_num': math.ceil(total_num/10)})


def add_project(request):
	"""
	添加项目
	"""
	if request.method == 'POST':
		name = request.POST.get('name')
		user_name = request.user.username
		if name:
			if Projects.objects.filter(type='ATI', name=name):
				logger.warning('项目已存在，请勿重复添加')
				return JsonResponse({'code': 1, 'msg': '项目已存在，请勿重复添加！', 'data': None})
			else:
				try:
					desc = request.POST.get('description')
					pro_id = str(int(time.time() * 10000))
					Projects.objects.create(id=pro_id, name=name, description=desc, type='ATI', create_time=time_strftime(), update_time=time_strftime())
					project_id = Projects.objects.get(type='ATI', name=name).id
					UserProject.objects.create(user_name=user_name, project_id=project_id, type='ATI', create_time=time_strftime())
					logger.info(f'{user_name}---{name}项目创建成功')
					return JsonResponse({'code': 0, 'msg': '项目创建成功', 'data': None})
				except Exception as err:
					logger.error(err)
					logger.error(traceback.format_exc())
					return JsonResponse({'code': 1, 'msg': '项目创建失败，请检查参数是否正确', 'data': None})
		else:
			logger.error('项目名称不能为空')
			return JsonResponse({'code': 1, 'msg': '项目名称不能为空', 'data': None})
	if request.method == 'GET':
		return render(request, 'ATI/project/add.html')


def update_project(request):
	"""
	更新项目信息
	"""
	if request.method == 'POST':
		try:
			name = request.POST.get('name')
			user_name = request.user.username
			r = Projects.objects.get(type='ATI', name=name)
			r.name = name
			r.description = request.POST.get('description')
			r.update_time = time_strftime()
			r.save()
			logger.info(f'{user_name}---项目保存成功')
			return JsonResponse({'code': 0, 'msg': '项目保存成功', 'data': None})
		except Exception as err:
			logger.error(err)
			logger.error(traceback.format_exc())
			return JsonResponse({'code': 1, 'msg': '项目更新失败', 'data': None})

	if request.method == 'GET':
		name = request.GET.get('name')
		projects = Projects.objects.get(type='ATI', name=name)
		return render(request, 'ATI/project/update.html', context={'projects': projects})


def delete_project(request):
	"""
	删除项目
	"""
	if request.method == "GET":
		user_name = request.user.username
		try:
			name = request.GET.get('name')
			Projects.objects.get(type='ATI', name=name).delete()
			logger.info(f'{user_name}---{name}项目删除成功')
			return JsonResponse({'code': 0, 'msg': '项目删除成功', 'data': None})
		except ProtectedError as err:
			logger.info(err)
			return JsonResponse({'code': 2, 'msg': '变量删除失败，由于存在受保护的外键', 'data': None})
		except Exception as err:
			logger.error(err)
			logger.error(traceback.format_exc())
			return JsonResponse({'code': 1, 'msg': '项目删除失败', 'data': None})


def manager_project(request):
	"""
	添加项目成员
	"""
	if request.method == 'GET':
		name = request.GET.get('name')
		project_id = Projects.objects.get(type='ATI', name=name).id
		user_list = UserProject.objects.filter(project_id=project_id).values_list('user_name')
		users = [r[0] for r in user_list]
		return render(request, 'ATI/project/manager.html', context={'projects': name, 'user_list': ', '.join(users)})

	if request.method == 'POST':
		name = request.POST.get('name')
		username = request.POST.get('username')
		current_user = request.user.username
		if User.objects.filter(username=username):
			project_id = Projects.objects.get(type='ATI', name=name).id
			if project_id:
				if request.POST.get('isadd') == '0':
					try:
						UserProject.objects.get(project_id=project_id, user_name=username).delete()
						logger.info(f'{current_user}---{name}项目中的{username}用户删除成功')
						return JsonResponse({'code': 0, 'msg': '删除成功', 'data': None})
					except Exception as err:
						logger.error(err)
						return JsonResponse({'code': 1, 'msg': '该用户已不在该项目中', 'data': None})

				if request.POST.get('isadd') == '1':
					if UserProject.objects.filter(project_id=project_id, user_name=username):
						return JsonResponse({'code': 1, 'msg': '该用户已在项目中', 'data': None})
					else:
						UserProject.objects.create(user_name=username, project_id=project_id, type='ATI', create_time=time_strftime())
						logger.info(f'{current_user}---{name}项目添加{username}用户成功')
						return JsonResponse({'code': 0, 'msg': '添加成功', 'data': None})
			else:
				logger.error('该项目不存在，请先创建')
				return JsonResponse({'code': 1, 'msg': '该项目不存在，请先创建', 'data': None})
		else:
			logger.error('该用户不存在，请检查用户名输入是否正确，或用户是否已注册')
			return JsonResponse({'code': 1, 'msg': '该用户不存在，请检查用户名输入是否正确，或用户是否已注册', 'data': None})


def interfaces(request):
	"""
	查询接口
	"""
	if request.method == 'GET':
		project_id = request.GET.get('projectId')
		page_num = request.GET.get('pageNum')
		content = request.GET.get('Content', default="")
		if page_num:
			page_num = int(page_num)
		else:
			page_num = 1

		user_name = request.user.username
		start_index = (page_num - 1) * 10
		end_index = page_num * 10

		project_name = Projects.objects.get(type='ATI', id=project_id).name

		if content:
			total_num = Interfaces.objects.filter(Q(project_id=project_id), Q(name__contains=content) | Q(interface__contains=content) | Q(interface_id__contains=content)).count()
			interface_list = Interfaces.objects.filter(Q(project_id=project_id), Q(name__contains=content) | Q(interface__contains=content) | Q(interface_id__contains=content)).order_by('-update_time')[start_index:end_index]
		else:
			total_num = Interfaces.objects.filter(project_id=project_id).count()
			interface_list = Interfaces.objects.filter(project_id=project_id).order_by('-update_time')[start_index:end_index]

		return render(request, 'ATI/interface/index.html', context={'username': user_name, 'interface_list': interface_list, 'project_name': project_name, 'project_id': project_id, 'content': content, 'page_num': page_num, 'total_num': math.ceil(total_num / 10)})


def add_interface(request):
	"""
	添加接口
	"""
	if request.method == 'POST':
		interface_id = request.POST.get('interface_id')
		interface = request.POST.get('interface')
		project_id = request.POST.get('project_id')
		user_name = request.user.username
		if interface_id:
			if interface:
				if Interfaces.objects.filter(interface_id=interface_id, project_id=project_id):
					logger.warning('接口ID已存在，请勿重复添加')
					return JsonResponse({'code': 1, 'msg': '接口ID已存在，请勿重复添加！', 'data': None})
				else:
					try:
						timeout = request.POST.get('timeout') if request.POST.get('timeout') else 500
						Interfaces.objects.create(
							interface_id=interface_id, project_id=project_id, name=request.POST.get('name'),
							interface=interface, protocol=request.POST.get('protocol'),
							method=request.POST.get('method'), parameter=request.POST.get('parameter'),
							timeout=timeout, header=request.POST.get('header'),
							pre_process=request.POST.get('pre_process'), post_process=request.POST.get('post_process'),
							expect_result=request.POST.get('expect_result'), assert_method=request.POST.get('assert_method'),
							true_result=request.POST.get('true_result'), description=request.POST.get('description'),
							created_by=user_name, updated_by=user_name, create_time=time_strftime(),
							update_time=time_strftime()
						)
						logger.info(f'{user_name}---{interface_id}接口创建成功')
						return JsonResponse({'code': 0, 'msg': '接口创建成功', 'data': None})
					except Exception as err:
						logger.error(err)
						logger.error(traceback.format_exc())
						return JsonResponse({'code': 1, 'msg': '接口新增异常，请检查参数是否正确', 'data': None})
			else:
				logger.error('接口url不能为空')
				return JsonResponse({'code': 1, 'msg': '接口url不能为空', 'data': None})
		else:
			logger.error('接口ID不能为空')
			return JsonResponse({'code': 1, 'msg': '接口ID不能为空', 'data': None})
	if request.method == 'GET':
		project_id = request.GET.get('projectId')
		user_name = request.user.username
		return render(request, 'ATI/interface/add.html', context={'username': user_name, 'project_id': project_id})


def edit_interface(request):
	"""
	编辑接口
	"""
	if request.method == 'POST':
		try:
			interface_id = request.POST.get('interface_id')
			project_id = request.POST.get('project_id')
			user_name = request.user.username
			r = Interfaces.objects.get(interface_id=interface_id, project_id=project_id)
			r.name = request.POST.get('name')
			r.interface = request.POST.get('interface')
			r.protocol = request.POST.get('protocol')
			r.method = request.POST.get('method')
			r.parameter = request.POST.get('parameter')
			r.timeout = request.POST.get('timeout') if request.POST.get('timeout') else 500
			r.header = request.POST.get('header')
			r.pre_process = request.POST.get('pre_process')
			r.post_process = request.POST.get('post_process')
			r.expect_result = request.POST.get('expect_result')
			r.assert_method = request.POST.get('assert_method')
			r.true_result = request.POST.get('true_result')
			r.description = request.POST.get('description')
			r.updated_by = user_name
			r.update_time = time_strftime()
			r.save()
			logger.info(f'{user_name}---{interface_id}接口修改成功')
			return JsonResponse({'code': 0, 'msg': '接口修改成功', 'data': None})
		except Exception as err:
			logger.error(err)
			logger.error(traceback.format_exc())
			return JsonResponse({'code': 1, 'msg': '接口保存异常，请检查参数是否正确', 'data': None})

	if request.method == 'GET':
		interface_id = request.GET.get('Id')
		project_id = request.GET.get('projectId')
		copy = request.GET.get('copy')
		user_name = request.user.username
		interface = Interfaces.objects.get(interface_id=interface_id, project_id=project_id)
		return render(request, 'ATI/interface/edit.html', context={'interface': interface, 'username': user_name, 'project_id': project_id, 'copy': copy})


def delete_interface(request):
	"""
		删除接口
	"""
	if request.method == "GET":
		interface_id = request.GET.get('Id')
		project_id = request.GET.get('projectId')
		user_name = request.user.username
		try:
			Interfaces.objects.get(project_id=project_id, interface_id=interface_id).delete()
			logger.info(f'{user_name}---{interface_id}接口删除成功')
			return JsonResponse({'code': 0, 'msg': '接口删除成功', 'data': None})
		except ProtectedError as err:
			logger.info(err)
			return JsonResponse({'code': 2, 'msg': '接口删除失败，由于存在受保护的外键', 'data': None})
		except Exception as err:
			logger.error(err)
			logger.error(traceback.format_exc())
			return JsonResponse({'code': 1, 'msg': '接口删除失败', 'data': None})


def scenes(request):
	"""
	查询场景
	"""
	if request.method == 'GET':
		project_id = request.GET.get('projectId')
		page_num = request.GET.get('pageNum')
		content = request.GET.get('Content', default="")
		if page_num:
			page_num = int(page_num)
		else:
			page_num = 1

		user_name = request.user.username
		start_index = (page_num - 1) * 10
		end_index = page_num * 10

		project_name = Projects.objects.get(type='ATI', id=project_id).name

		if content:
			total_num = Scenes.objects.filter(Q(project_id=project_id), Q(name__contains=content)).count()
			scene_list = Scenes.objects.filter(Q(project_id=project_id), Q(name__contains=content)).order_by('-update_time')[start_index:end_index]
		else:
			total_num = Scenes.objects.filter(project_id=project_id).count()
			scene_list = Scenes.objects.filter(project_id=project_id).order_by('-update_time')[start_index:end_index]

		return render(request, 'ATI/scenes/index.html', context={'username': user_name, 'scene_list': scene_list, 'project_name': project_name, 'project_id': project_id, 'content': content, 'page_num': page_num, 'total_num': math.ceil(total_num / 10)})


def add_scene(request):
	"""
		添加场景
	"""
	if request.method == 'POST':
		name = request.POST.get('name')
		project_id = request.POST.get('project_id')
		user_name = request.user.username
		if name:
			if Scenes.objects.filter(name=name, project_id=project_id):
				logger.warning('场景已存在，请勿重复添加')
				return JsonResponse({'code': 1, 'msg': '场景已存在，请勿重复添加！', 'data': None})
			else:
				try:
					desc = request.POST.get('description')
					cas_id = str(int(time.time() * 10000))
					Scenes.objects.create(id=cas_id, name=name, description=desc, project_id=project_id, created_by=user_name, updated_by=user_name, create_time=time_strftime(), update_time=time_strftime())
					logger.info(f'{user_name}---{name}用例创建成功')
					return JsonResponse({'code': 0, 'msg': '场景创建成功', 'data': None})
				except Exception as err:
					logger.error(err)
					logger.error(traceback.format_exc())
					return JsonResponse({'code': 1, 'msg': '场景创建失败，请检查参数是否正确', 'data': None})
		else:
			logger.error('场景名称不能为空')
			return JsonResponse({'code': 1, 'msg': '场景名称不能为空', 'data': None})
	if request.method == 'GET':
		project_id = request.GET.get('projectId')
		user_name = request.user.username
		return render(request, 'ATI/scenes/add.html', context={'username': user_name, 'project_id': project_id})


def edit_scene(request):
	"""
	编辑场景
	"""
	if request.method == 'POST':
		try:
			scene_id = request.POST.get('Id')
			project_id = request.POST.get('project_id')
			name = request.POST.get('name')
			user_name = request.user.username
			r = Scenes.objects.get(id=scene_id, project_id=project_id)
			r.name = name
			r.description = request.POST.get('description')
			r.update_time = time_strftime()
			r.updated_by = user_name
			r.save()
			logger.info(f'{user_name}---场景{name}修改成功')
			return JsonResponse({'code': 0, 'msg': '场景修改成功', 'data': None})
		except Exception as err:
			logger.error(err)
			logger.error(traceback.format_exc())
			return JsonResponse({'code': 1, 'msg': '场景修改失败，请检查参数是否正确', 'data': None})

	if request.method == 'GET':
		user_name = request.user.username
		project_id = request.GET.get('projectId')
		case_id = request.GET.get('Id')
		project_name = Projects.objects.get(id=project_id, type='ATI').name
		scenes = Scenes.objects.get(id=case_id, project_id=project_id)
		return render(request, 'ATI/scenes/edit.html', context={'username': user_name, 'scenes': scenes, 'project_name': project_name , 'project_id': project_id})


def delete_scene(request):
	"""
	删除场景
	"""
	if request.method == "GET":
		case_id = request.GET.get('Id')
		project_id = request.GET.get('projectId')
		user_name = request.user.username
		try:
			Scenes.objects.get(project_id=project_id, id=case_id).delete()
			logger.info(f'{user_name}---{case_id}场景删除成功')
			return JsonResponse({'code': 0, 'msg': '场景删除成功', 'data': None})
		except ProtectedError as err:
			logger.info(err)
			return JsonResponse({'code': 2, 'msg': '场景删除失败，由于存在受保护的外键', 'data': None})
		except Exception as err:
			logger.error(err)
			logger.error(traceback.format_exc())
			return JsonResponse({'code': 1, 'msg': '场景删除失败', 'data': None})


def show_scene_interface(request):
	"""
		查看用例中的接口
	"""
	scene_id = request.GET.get('Id')
	project_id = request.GET.get('projectId')
	page_num = request.GET.get('pageNum')
	if page_num:
		page_num = int(page_num)
	else:
		page_num = 1

	user_name = request.user.username
	start_index = (page_num - 1) * 10
	end_index = page_num * 10
	total_num = InterfaceScene.objects.filter(scene_id=scene_id).count()
	scene_interfaces = InterfaceScene.objects.filter(scene_id=scene_id).order_by('display_sort')[start_index:end_index]
	return render(request, 'ATI/scenes/interfaces.html', context={'username': user_name, 'project_id': project_id, 'scene_id': scene_id, 'scene_interfaces': scene_interfaces, 'page_num': page_num, 'total_num': math.ceil(total_num / 10)})


def add_scene_interface(request):
	"""
	给用例增加接口，查看接口列表
	"""
	if request.method == 'GET':
		project_id = request.GET.get('projectId')
		scene_id = request.GET.get('sceneId')
		page_num = request.GET.get('pageNum')
		content = request.GET.get('Content', default="")
		if page_num:
			page_num = int(page_num)
		else:
			page_num = 1

		user_name = request.user.username
		start_index = (page_num - 1) * 10
		end_index = page_num * 10

		project_name = Projects.objects.get(type='ATI', id=project_id).name

		if content:
			total_num = Interfaces.objects.filter(Q(project_id=project_id), Q(name__contains=content) | Q(interface__contains=content) | Q(interface_id__contains=content)).count()
			interface_list = Interfaces.objects.filter(Q(project_id=project_id), Q(name__contains=content) | Q(interface__contains=content) | Q(interface_id__contains=content)).order_by('-update_time')[start_index:end_index]
		else:
			total_num = Interfaces.objects.filter(project_id=project_id).count()
			interface_list = Interfaces.objects.filter(project_id=project_id).order_by('-update_time')[start_index:end_index]

		return render(request, 'ATI/scenes/add_interface.html', context={'username': user_name, 'interface_list': interface_list, 'project_name': project_name, 'project_id': project_id, 'scene_id': scene_id, 'content': content, 'page_num': page_num, 'total_num': math.ceil(total_num / 10)})


def add_interface_to_scene(request):
	"""
	给用例增加接口
	"""
	try:
		user_name = request.user.username
		scene_id = request.POST.get('sceneId')
		interface_id = request.POST.get('interfaceId')
		total_num = InterfaceScene.objects.filter(scene_id=scene_id).aggregate(Max('display_sort'))['display_sort__max']

		if not total_num:
			total_num = 0

		InterfaceScene.objects.create(scene_id=scene_id, interface_id=interface_id, is_run=1, display_sort=total_num+1)
		logger.info(f'{user_name}---将接口{interface_id}添加到用例{scene_id}中')
		return JsonResponse({'code': 0, 'msg': '接口添加成功', 'data': None})
	except Exception as err:
		logger.error(err)
		logger.error(traceback.format_exc())
		return JsonResponse({'code': 1, 'msg': '接口添加异常', 'data': None})


def set_is_run(request):
	"""
	设置测试场景中的接口是否执行
	"""
	try:
		user_name = request.user.username
		scene_id = request.POST.get('sceneId')
		interface_id = request.POST.get('interfaceId')
		is_run = request.POST.get('isRun')
		if scene_id:
			r = Scenes.objects.get(id=scene_id)
			r.is_run = is_run
			r.save()
			logger.info(f'{user_name}----{scene_id}是否执行设置为{is_run}')
		if interface_id:
			r = InterfaceScene.objects.get(id=interface_id)
			r.is_run = is_run
			r.save()
			logger.info(f'{user_name}----{interface_id}是否执行设置为{is_run}')

		return JsonResponse({'code': 0, 'msg': '设置成功', 'data': None})

	except Exception as err:
		logger.error(err)
		return JsonResponse({'code': 1, 'msg': '未设置成功', 'data': None})


def move_up_or_down(request):
	"""
	向上或向下移动
	"""
	try:
		user_name = request.user.username
		scene_id = request.POST.get('sceneId')
		interface_id = request.POST.get('interfaceId')
		is_up = request.POST.get('is_up')
		if is_up == '0':
			current_sort = InterfaceScene.objects.get(scene_id=scene_id, interface_id=interface_id).display_sort
			downer = InterfaceScene.objects.filter(scene_id=scene_id, display_sort__gt=current_sort).order_by('display_sort').first().id
			r = InterfaceScene.objects.get(scene_id=scene_id, interface_id=interface_id)
			r.display_sort = current_sort + 1
			r.save()

			r = InterfaceScene.objects.get(id=downer)
			r.display_sort = current_sort
			r.save()

			logger.info(f'{user_name}---用例{scene_id}向下移动成功')

		else:
			current_sort = InterfaceScene.objects.get(scene_id=scene_id, interface_id=interface_id).display_sort
			upper = InterfaceScene.objects.filter(scene_id=scene_id, display_sort__lt=current_sort).order_by('display_sort').last().id
			r = InterfaceScene.objects.get(scene_id=scene_id, interface_id=interface_id)
			r.display_sort = current_sort - 1
			r.save()

			r = InterfaceScene.objects.get(id=upper)
			r.display_sort = current_sort
			r.save()

			logger.info(f'{user_name}---用例{scene_id}向上移动成功')

		return JsonResponse({'code': 0, 'msg': '移动成功', 'data': None})

	except AttributeError as err:
		logger.error(err)
		return JsonResponse({'code': 0, 'msg': '移动成功', 'data': None})

	except Exception as err:
		logger.error(err)
		logger.error(traceback.format_exc())
		return JsonResponse({'code': 1, 'msg': '移动失败', 'data': None})


def delete_interface_from_scene(request):
	"""
	从场景中删除接口
	"""
	user_name = request.user.username
	ID = request.GET.get('Id')
	scene_id = request.GET.get('sceneId')
	interface_id = request.GET.get('interfaceId')
	try:
		InterfaceScene.objects.get(id=ID, interface_id=interface_id).delete()
		logger.info(f'{user_name}---接口{interface_id}从场景{scene_id}中删除')
		return JsonResponse({'code': 0, 'msg': '删除成功', 'data': None})
	except Exception as err:
		logger.error(err)
		logger.error(traceback.format_exc())
		return JsonResponse({'code': 1, 'msg': '删除失败', 'data': None})


def variables(request):
	"""
		查询当前用户下所有的全局变量
		:param request:
		:return:
	"""
	if request.method == 'GET':
		plan_id = request.GET.get('Id')
		project_id = request.GET.get('projectId')
		page_num = request.GET.get('pageNum')
		if page_num:
			page_num = int(page_num)
		else:
			page_num = 1

		user_name = request.user.username
		start_index = (page_num - 1) * 10
		end_index = page_num * 10

		total_num = Variables.objects.filter(plan_id=plan_id).count()
		global_list = Variables.objects.filter(plan_id=plan_id).order_by('-update_time')[start_index:end_index]

		return render(request, 'ATI/variable/index.html', context={'username': user_name, 'global_list': global_list, 'plan_id': plan_id, 'project_id': project_id, 'page_num': page_num, 'total_num': math.ceil(total_num / 10)})


def add_variable(request):
	"""
		添加变量
		"""
	if request.method == 'POST':
		name = request.POST.get('name')
		plan_id = request.POST.get('plan_id')
		user_name = request.user.username
		if name:
			if Variables.objects.filter(name=name, plan_id=plan_id):
				logger.warning('变量已存在，请勿重复添加')
				return JsonResponse({'code': 1, 'msg': '变量已存在，请勿重复添加！', 'data': None})
			else:
				try:
					value_v = request.POST.get('value')
					desc = request.POST.get('description')
					Variables.objects.create(name=name, description=desc, value=value_v, plan_id=plan_id, create_time=time_strftime(),
											created_by=user_name, updated_by=user_name, update_time=time_strftime())
					logger.info(f'{user_name}---{name}变量创建成功')
					return JsonResponse({'code': 0, 'msg': '变量创建成功', 'data': None})
				except Exception as err:
					logger.error(err)
					logger.error(traceback.format_exc())
					return JsonResponse({'code': 1, 'msg': '变量创建失败，请检查参数是否正确', 'data': None})
		else:
			logger.error('变量名称不能为空')
			return JsonResponse({'code': 1, 'msg': '变量名称不能为空', 'data': None})
	if request.method == 'GET':
		user_name = request.user.username
		plan_id = request.GET.get('Id')
		project_id = request.GET.get('projectId')
		return render(request, 'ATI/variable/add.html', context={'username': user_name, 'plan_id': plan_id, 'project_id': project_id})


def edit_variable(request):
	"""
		编辑变量
	"""
	if request.method == 'POST':
		try:
			name = request.POST.get('name')
			plan_id = request.POST.get('plan_id')
			user_name = request.user.username
			r = Variables.objects.get(name=name, plan_id=plan_id)
			r.value = request.POST.get('value')
			r.description = request.POST.get('description')
			r.update_time = time_strftime()
			r.updated_by = user_name
			r.save()
			logger.info(f'{user_name}---变量{name}修改成功')
			return JsonResponse({'code': 0, 'msg': '变量修改成功', 'data': None})
		except Exception as err:
			logger.error(err)
			logger.error(traceback.format_exc())
			return JsonResponse({'code': 1, 'msg': '变量修改失败，请检查参数是否正确', 'data': None})

	if request.method == 'GET':
		name = request.GET.get('name')
		plan_id = request.GET.get('planId')
		project_id = request.GET.get('projectId')
		variables = Variables.objects.get(name=name, plan_id=plan_id)
		return render(request, 'ATI/variable/edit.html', context={'variables': variables, 'plan_id': plan_id, 'project_id': project_id})


def delete_variable(request):
	"""
		删除变量
	"""
	if request.method == "GET":
		name = request.GET.get('name')
		plan_id = request.GET.get('planId')
		user_name = request.user.username
		try:
			Variables.objects.get(plan_id=plan_id, name=name).delete()
			logger.info(f'{user_name}---{name}变量删除成功')
			return JsonResponse({'code': 0, 'msg': '变量删除成功', 'data': None})
		except Exception as err:
			logger.error(err)
			logger.error(traceback.format_exc())
			return JsonResponse({'code': 1, 'msg': '变量删除失败', 'data': None})


def plans(request):
	"""
	测试计划
	"""
	if request.method == 'GET':
		project_id = request.GET.get('projectId')
		page_num = request.GET.get('pageNum')
		content = request.GET.get('Content', default="")
		if page_num:
			page_num = int(page_num)
		else:
			page_num = 1

		user_name = request.user.username
		url = request.headers['Host']
		start_index = (page_num - 1) * 10
		end_index = page_num * 10

		project_name = Projects.objects.get(type='ATI', id=project_id).name

		if content:
			total_num = Plans.objects.filter(Q(project_id=project_id), Q(name__contains=content)).count()
			plan_list = Plans.objects.filter(Q(project_id=project_id), Q(name__contains=content)).order_by('-update_time')[start_index:end_index]
		else:
			total_num = Plans.objects.filter(project_id=project_id).count()
			plan_list = Plans.objects.filter(project_id=project_id).order_by('-update_time')[start_index:end_index]

		return render(request, 'ATI/plan/index.html', context={'username': user_name, 'plan_list': plan_list, 'project_name': project_name, 'project_id': project_id, 'content': content, 'url':url, 'page_num': page_num, 'total_num': math.ceil(total_num / 10)})


def add_plan(request):
	"""
	添加测试计划
	"""
	if request.method == 'POST':
		name = request.POST.get('name')
		project_id = request.POST.get('project_id')
		user_name = request.user.username
		url = request.headers['Host']
		if name:
			if Plans.objects.filter(name=name, project_id=project_id):
				logger.warning('测试计划已存在，请勿重复添加')
				return JsonResponse({'code': 1, 'msg': '测试计划已存在，请勿重复添加！', 'data': None})
			else:
				try:
					desc = request.POST.get('description')
					timing = request.POST.get('timing')
					interval = request.POST.get('interval')
					time_setting = request.POST.get('time_setting')
					sending = request.POST.get('sending')
					receiver_name = request.POST.get('receiver_name')
					subject = request.POST.get('subject')
					receiver_email = request.POST.get('receiver_email')

					if sending == "0":
						email = ""
					else:
						email = json.dumps({
							'subject': subject,
							'receiver_name': receiver_name,
							'receiver_email': receiver_email
						}, ensure_ascii=False)

					if timing == "0":
						time_set = ""
					elif timing == "2":
						time_set = interval
					else:
						time_set = time_setting
					plan_id = str(int(time.time() * 10000))
					Plans.objects.create(id=plan_id, name=name, description=desc, project_id=project_id,
										 timing=timing, time_set=time_set, is_email=sending, email=email,
										 created_by=user_name, updated_by=user_name, is_running=0, last_run_time=0,
										 host=url, create_time=time_strftime(), update_time=time_strftime())
					logger.info(f'{user_name}---{name}测试计划创建成功')
					return JsonResponse({'code': 0, 'msg': '测试计划创建成功', 'data': None})
				except Exception as err:
					logger.error(err)
					logger.error(traceback.format_exc())
					return JsonResponse({'code': 1, 'msg': '测试计划创建失败，请检查参数是否正确', 'data': None})
		else:
			logger.error('测试计划名称不能为空')
			return JsonResponse({'code': 1, 'msg': '测试计划名称不能为空', 'data': None})
	if request.method == 'GET':
		project_id = request.GET.get('projectId')
		user_name = request.user.username
		return render(request, 'ATI/plan/add.html', context={'username': user_name, 'project_id': project_id})


def edit_plan(request):
	"""
	编辑测试计划
	"""
	if request.method == 'POST':
		try:
			plan_id = request.POST.get('Id')
			name = request.POST.get('name')
			project_id = request.POST.get('project_id')
			user_name = request.user.username
			timing = request.POST.get('timing')
			sending = request.POST.get('sending')

			interval = request.POST.get('interval')
			time_setting = request.POST.get('time_setting')
			receiver_name = request.POST.get('receiver_name')
			subject = request.POST.get('subject')
			receiver_email = request.POST.get('receiver_email')

			if sending == "0":
				email = ""
			else:
				email = json.dumps({
					'subject': subject,
					'receiver_name': receiver_name,
					'receiver_email': receiver_email
				}, ensure_ascii=False)

			if timing == "0":
				time_set = ""
			elif timing == "2":
				time_set = interval
			else:
				time_set = time_setting
			r = Plans.objects.get(id=plan_id, project_id=project_id)
			r.description = request.POST.get('description')
			r.name = name
			r.timing = timing
			r.time_set = time_set
			r.is_email = sending
			r.email = email
			r.update_by = user_name
			r.update_time = time_strftime()
			r.save()

			logger.info(f'{user_name}---{name}测试计划编辑成功')
			return JsonResponse({'code': 0, 'msg': '测试计划编辑成功', 'data': None})
		except Exception as err:
			logger.error(err)
			logger.error(traceback.format_exc())
			return JsonResponse({'code': 1, 'msg': '测试计划编辑失败，请检查参数是否正确', 'data': None})

	if request.method == 'GET':
		user_name = request.user.username
		plan_id = request.GET.get('Id')
		project_id = request.GET.get('projectId')
		plan = Plans.objects.get(id=plan_id, project_id=project_id)
		if plan.email:
			email = json.loads(plan.email)
			receiver_name = email.get('receiver_name')
			subject = email.get('subject')
			receiver_email = email.get('receiver_email')
		else:
			receiver_name = None
			subject = None
			receiver_email = None
		return render(request, 'ATI/plan/edit.html', context={'username': user_name, 'project_id': project_id, 'plan': plan, 'subject': subject, 'receiver_name': receiver_name, 'receiver_email': receiver_email})


def copy_plan(request):
	"""
	复制测试计划
	"""
	try:
		user_name = request.user.username
		plan_id = request.GET.get('Id')
		plan = Plans.objects.get(id=plan_id)
		plan_id_id = str(int(time.time() * 10000))
		plan_name = plan.name + '_copy'
		Plans.objects.create(id=plan_id_id, name=plan_name, description=plan.description, project_id=plan.project_id,
							 timing=plan.timing, time_set=plan.time_set, is_email=plan.is_email, email=plan.email,
							 is_running=0, last_run_time=0, host=plan.host, created_by=user_name, updated_by=user_name,
							 create_time=time_strftime(), update_time=time_strftime())
		logger.info(f'{user_name}---{plan_name}测试计划创建成功')

		scenes = ScenePlan.objects.filter(plan_id=plan_id)
		for scene in scenes:
			ScenePlan.objects.create(is_run=scene.is_run, display_sort=scene.display_sort, scene_id=scene.scene_id, plan_id=plan_id_id)
		logger.info(f'{user_name}---{plan_name}测试计划中的测试场景创建成功')
		return JsonResponse({'code': 0, 'msg': '测试计划复制成功', 'data': None})
	except Exception as err:
		logger.error(err)
		logger.error(traceback.format_exc())
		return JsonResponse({'code': 1, 'msg': '测试计划复制失败', 'data': None})


def delete_plan(request):
	"""
		删除计划
	"""
	if request.method == "GET":
		name = request.GET.get('name')
		project_id = request.GET.get('projectId')
		user_name = request.user.username
		try:
			Plans.objects.get(project_id=project_id, name=name).delete()
			logger.info(f'{user_name}---{name}测试计划删除成功')
			return JsonResponse({'code': 0, 'msg': '测试计划删除成功', 'data': None})
		except ProtectedError as err:
			logger.info(err)
			return JsonResponse({'code': 2, 'msg': '测试计划删除失败，由于存在受保护的外键', 'data': None})
		except Exception as err:
			logger.error(err)
			logger.error(traceback.format_exc())
			return JsonResponse({'code': 1, 'msg': '测试计划删除失败', 'data': None})


def show_plan_and_scene(request):
	"""
	查看测试计划中的测试场景
	"""
	if request.method == 'GET':
		user_name = request.user.username
		plan_id = request.GET.get('Id')
		project_id = request.GET.get('projectId')
		page_num = request.GET.get('pageNum')
		if page_num:
			page_num = int(page_num)
		else:
			page_num = 1

		start_index = (page_num - 1) * 10
		end_index = page_num * 10
		total_num = ScenePlan.objects.filter(plan_id=plan_id).count()
		plan_scenes = ScenePlan.objects.filter(plan_id=plan_id).order_by('display_sort')[start_index:end_index]
		return render(request, 'ATI/plan/scenes.html', context={'username': user_name, 'project_id': project_id, 'plan_id': plan_id, 'plan_scenes': plan_scenes, 'page_num': page_num, 'total_num': math.ceil(total_num / 10)})


def add_plan_and_scene(request):
	"""
	给测试计划添加测试用例，显示测试用例列表
	"""
	if request.method == 'GET':
		project_id = request.GET.get('projectId')
		plan_id = request.GET.get('planId')
		page_num = request.GET.get('pageNum')
		content = request.GET.get('Content', default="")
		if page_num:
			page_num = int(page_num)
		else:
			page_num = 1

		user_name = request.user.username
		start_index = (page_num - 1) * 10
		end_index = page_num * 10

		project_name = Projects.objects.get(type='ATI', id=project_id).name

		if content:
			total_num = Scenes.objects.filter(Q(project_id=project_id), Q(name__contains=content)).count()
			scene_list = Scenes.objects.filter(Q(project_id=project_id), Q(name__contains=content)).order_by('-update_time')[start_index:end_index]
		else:
			total_num = Scenes.objects.filter(project_id=project_id).count()
			scene_list = Scenes.objects.filter(project_id=project_id).order_by('-update_time')[start_index:end_index]

		return render(request, 'ATI/plan/add_scene.html', context={'username': user_name, 'scene_list': scene_list, 'project_name': project_name, 'plan_id': plan_id,
							   'project_id': project_id, 'content': content, 'page_num': page_num, 'total_num': math.ceil(total_num / 10)})


def add_scene_to_plan(request):
	"""
	把测试场景添加到测试计划中
	"""
	try:
		user_name = request.user.username
		scene_id = request.POST.get('sceneId')
		plan_id = request.POST.get('planId')
		total_num = ScenePlan.objects.filter(plan_id=plan_id).aggregate(Max('display_sort'))['display_sort__max']

		if not total_num:
			total_num = 0

		ScenePlan.objects.create(plan_id=plan_id, scene_id=scene_id, is_run=1, display_sort=total_num+1)
		logger.info(f'{user_name}---将测试场景{scene_id}添加到测试计划{plan_id}中')
		return JsonResponse({'code': 0, 'msg': '测试场景添加成功', 'data': None})
	except Exception as err:
		logger.error(err)
		logger.error(traceback.format_exc())
		return JsonResponse({'code': 1, 'msg': '测试场景添加异常', 'data': None})


def edit_scene_from_plan(request):
	"""
	在测试计划中编辑测试场景
	"""
	scene_id = request.GET.get('Id')
	project_id = request.GET.get('projectId')
	page_num = request.GET.get('pageNum')
	if page_num:
		page_num = int(page_num)
	else:
		page_num = 1

	user_name = request.user.username
	start_index = (page_num - 1) * 10
	end_index = page_num * 10
	total_num = InterfaceScene.objects.filter(case_id=scene_id).count()
	scene_interfaces = InterfaceScene.objects.filter(case_id=scene_id).order_by('display_sort')[start_index:end_index]
	return render(request, 'ATI/plan/interfaces.html', context={'username': user_name, 'project_id': project_id, 'scene_id': scene_id, 'scene_interfaces': scene_interfaces, 'page_num': page_num, 'total_num': math.ceil(total_num / 10)})


def delete_scene_from_plan(request):
	"""
	从测试计划中删除测试场景
	"""
	user_name = request.user.username
	ID = request.GET.get('Id')
	try:
		ScenePlan.objects.get(id=ID).delete()
		logger.info(f'{user_name}---测试场景{ID}从测试计划中删除')
		return JsonResponse({'code': 0, 'msg': '删除成功', 'data': None})
	except Exception as err:
		logger.error(err)
		logger.error(traceback.format_exc())
		return JsonResponse({'code': 1, 'msg': '删除失败', 'data': None})


def set_is_run_scene(request):
	"""
	设置测试计划中的测试场景是否执行
	"""
	try:
		user_name = request.user.username
		scene_id = request.POST.get('sceneId')
		is_run = request.POST.get('isRun')
		r = ScenePlan.objects.get(id=scene_id)
		r.is_run = is_run
		r.save()
		logger.info(f'{user_name}----{scene_id}是否执行设置为{is_run}')
		return JsonResponse({'code': 0, 'msg': '设置成功', 'data': None})

	except Exception as err:
		logger.error(err)
		logger.error(traceback.format_exc())
		return JsonResponse({'code': 1, 'msg': '未设置成功', 'data': None})


def move_up_or_down_scene(request):
	"""
	向上或向下移动
	"""
	try:
		user_name = request.user.username
		scene_id = request.POST.get('sceneId')
		plan_id = request.POST.get('planId')
		is_up = request.POST.get('is_up')
		if is_up == '0':
			current_sort = ScenePlan.objects.get(scene_id=scene_id, plan_id=plan_id).display_sort
			downer = ScenePlan.objects.filter(plan_id=plan_id, display_sort__gt=current_sort).order_by('display_sort').first().id
			r = ScenePlan.objects.get(scene_id=scene_id, plan_id=plan_id)
			r.display_sort = current_sort + 1
			r.save()

			r = ScenePlan.objects.get(id=downer)
			r.display_sort = current_sort
			r.save()

			logger.info(f'{user_name}---测试场景{scene_id}向下移动成功')

		else:
			current_sort = ScenePlan.objects.get(scene_id=scene_id, plan_id=plan_id).display_sort
			upper = ScenePlan.objects.filter(plan_id=plan_id, display_sort__lt=current_sort).order_by('display_sort').last().id
			r = ScenePlan.objects.get(scene_id=scene_id, plan_id=plan_id)
			r.display_sort = current_sort - 1
			r.save()

			r = ScenePlan.objects.get(id=upper)
			r.display_sort = current_sort
			r.save()

			logger.info(f'{user_name}---测试场景{scene_id}向上移动成功')

		return JsonResponse({'code': 0, 'msg': '移动成功', 'data': None})

	except AttributeError as err:
		logger.error(err)
		return JsonResponse({'code': 0, 'msg': '移动成功', 'data': None})

	except Exception as err:
		logger.error(err)
		logger.error(traceback.format_exc())
		return JsonResponse({'code': 1, 'msg': '移动失败', 'data': None})


def show_result(request):
	"""
	展示测试结果
	"""
	if request.method == 'GET':
		page_num = request.GET.get('pageNum')
		content = request.GET.get('Content', default="")
		if page_num:
			page_num = int(page_num)
		else:
			page_num = 1

		user_name = request.user.username
		start_index = (page_num - 1) * 15
		end_index = page_num * 15

		status = ['未执行', '排队中', '执行中', '执行完成', '已取消', '执行失败']

		if content:
			total_num = Results.objects.filter(Q(type='ATI'), Q(plan_name__contains=content)).count()
			plan_list = Results.objects.filter(Q(type='ATI'), Q(plan_name__contains=content)).order_by('-start_time')[start_index:end_index]
		else:
			total_num = Results.objects.filter(type='ATI').count()
			plan_list = Results.objects.filter(type='ATI').order_by('-start_time')[start_index:end_index]

		return render(request, 'result/result.html', context={'username': user_name, 'plan_list': plan_list, 'content': content, 'status': status, 'page_num': page_num, 'total_num': math.ceil(total_num / 15)})

