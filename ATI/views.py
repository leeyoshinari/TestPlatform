import math
import time
import logging
import traceback
from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.clickjacking import xframe_options_sameorigin
from user.models import Projects, UserProject
from ATI.models import Variables, Interfaces, Cases, InterfaceCase, Plans, CasePlan
from common.timeFormat import time_strftime


logger = logging.getLogger('django')


def home(request):
	user_name = request.user.username
	return render(request, 'ATI/home.html', context={'username': user_name})


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
			if Projects.objects.filter(name=name, type='ATI'):
				logger.warning('项目已存在，请勿重复添加')
				return JsonResponse({'code': 1, 'msg': '项目已存在，请勿重复添加！', 'data': None})
			else:
				desc = request.POST.get('description')
				pro_id = str(int(time.time() * 10000))
				Projects.objects.create(id=pro_id, name=name, description=desc, type='ATI', create_time=time_strftime(), update_time=time_strftime())
				project_id = Projects.objects.get(name=name, type='ATI').id
				UserProject.objects.create(user_name=user_name, project_id=project_id, type='ATI', create_time=time_strftime())
				logger.info(f'{user_name}---{name}项目创建成功')
				return JsonResponse({'code': 0, 'msg': '项目创建成功', 'data': None})
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
		name = request.POST.get('name')
		user_name = request.user.username
		r = Projects.objects.get(name=name, type='ATI')
		r.name = name
		r.description = request.POST.get('description')
		r.update_time = time_strftime()
		r.save()
		logger.info(f'{user_name}---项目保存成功')
		return JsonResponse({'code': 0, 'msg': '项目保存成功', 'data': None})

	if request.method == 'GET':
		name = request.GET.get('name')
		projects = Projects.objects.get(name=name, type='ATI')
		return render(request, 'ATI/project/update.html', context={'projects': projects})


def del_project(request):
	"""
	删除项目
	"""
	if request.method == "GET":
		user_name = request.user.username
		try:
			name = request.GET.get('name')
			project_id = Projects.objects.get(name=name, type='ATI').id
			UserProject.objects.filter(project_id=project_id, type='ATI').delete()
			Projects.objects.get(name=name, type='ATI').delete()
			logger.info(f'{user_name}---{name}项目删除成功')
		except Exception as err:
			logger.error(err)
		return HttpResponseRedirect('/ATI/project/')


def manager_project(request):
	"""
	添加项目成员
	"""
	if request.method == 'GET':
		name = request.GET.get('name')
		project_id = Projects.objects.get(name=name, type='ATI').id
		user_list = UserProject.objects.filter(project_id=project_id, type='ATI').values_list('user_name')
		users = [r[0] for r in user_list]
		return render(request, 'ATI/project/manager.html', context={'projects': name, 'user_list': ', '.join(users)})

	if request.method == 'POST':
		name = request.POST.get('name')
		username = request.POST.get('username')
		current_user = request.user.username
		if User.objects.filter(username=username):
			project_id = Projects.objects.get(name=name, type='ATI').id
			if project_id:
				if request.POST.get('isadd') == '0':
					try:
						UserProject.objects.get(user_name=username, project_id=project_id, type='ATI').delete()
						logger.info(f'{current_user}---{name}项目中的{username}用户删除成功')
						return JsonResponse({'code': 0, 'msg': '删除成功', 'data': None})
					except Exception as err:
						logger.error(err)
						return JsonResponse({'code': 1, 'msg': '该用户已不在该项目中', 'data': None})

				if request.POST.get('isadd') == '1':
					if UserProject.objects.filter(user_name=username, project_id=project_id, type='ATI'):
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
		content = request.GET.get('Content')
		if page_num:
			page_num = int(page_num)
		else:
			page_num = 1

		user_name = request.user.username
		start_index = (page_num - 1) * 10
		end_index = page_num * 10

		project_name = Projects.objects.get(type='ATI', id=project_id).name

		if content:
			total_num = Interfaces.objects.filter(Q(project_id=project_id), Q(name__contains=content) | Q(interface__contains=content)).count()
			interface_list = Interfaces.objects.filter(Q(project_id=project_id), Q(name__contains=content) | Q(interface__contains=content)).order_by('-update_time')[start_index:end_index]
		else:
			total_num = Interfaces.objects.filter(project_id=project_id).count()
			interface_list = Interfaces.objects.filter(project_id=project_id).order_by('-update_time')[start_index:end_index]

		return render(request, 'ATI/interface/index.html', context={'username': user_name, 'interface_list': interface_list, 'project_name': project_name, 'project_id': project_id, 'page_num': page_num, 'total_num': math.ceil(total_num / 10)})


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
					timeout = request.POST.get('timeout') if request.POST.get('timeout') else 500
					Interfaces.objects.create(
						interface_id=interface_id, project_id=project_id, name=request.POST.get('name'),
						interface=interface, protocol=request.POST.get('protocol'),
						method=request.POST.get('method'), parameter=request.POST.get('parameter'),
						timeout=timeout, header=request.POST.get('header'),
						pre_process=request.POST.get('pre_process'), post_process=request.POST.get('post_process'),
						except_result=request.POST.get('except_result'), assert_method=request.POST.get('assert_method'),
						assert_result=request.POST.get('assert_result'), description=request.POST.get('description'),
						created_by=user_name, updated_by=user_name, create_time=time_strftime(),
						update_time=time_strftime()
					)
					logger.info(f'{user_name}---{interface_id}接口创建成功')
					return JsonResponse({'code': 0, 'msg': '接口创建成功', 'data': None})
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
		r.except_result = request.POST.get('except_result')
		r.assert_method = request.POST.get('assert_method')
		r.assert_result = request.POST.get('assert_result')
		r.description = request.POST.get('description')
		r.updated_by = user_name
		r.update_time = time_strftime()
		r.save()
		logger.info(f'{user_name}---{interface_id}接口修改成功')
		return JsonResponse({'code': 0, 'msg': '接口修改成功', 'data': None})

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
		except Exception as err:
			logger.error(err)
		return HttpResponseRedirect(f'/ATI/interface?projectId={project_id}')


def cases(request):
	"""
	查询用例
	"""
	if request.method == 'GET':
		project_id = request.GET.get('projectId')
		page_num = request.GET.get('pageNum')
		content = request.GET.get('Content')
		if page_num:
			page_num = int(page_num)
		else:
			page_num = 1

		user_name = request.user.username
		start_index = (page_num - 1) * 10
		end_index = page_num * 10

		project_name = Projects.objects.get(type='ATI', id=project_id).name

		if content:
			total_num = Cases.objects.filter(Q(project_id=project_id), Q(name__contains=content)).count()
			case_list = Cases.objects.filter(Q(project_id=project_id), Q(name__contains=content)).order_by('-update_time')[start_index:end_index]
		else:
			total_num = Cases.objects.filter(project_id=project_id).count()
			case_list = Cases.objects.filter(project_id=project_id).order_by('-update_time')[start_index:end_index]

		return render(request, 'ATI/cases/index.html', context={'username': user_name, 'case_list': case_list, 'project_name': project_name, 'project_id': project_id, 'page_num': page_num, 'total_num': math.ceil(total_num / 10)})


def add_case(request):
	"""
		添加用例
	"""
	if request.method == 'POST':
		name = request.POST.get('name')
		project_id = request.POST.get('project_id')
		user_name = request.user.username
		if name:
			if Cases.objects.filter(name=name, project_id=project_id):
				logger.warning('用例已存在，请勿重复添加')
				return JsonResponse({'code': 1, 'msg': '用例已存在，请勿重复添加！', 'data': None})
			else:
				desc = request.POST.get('description')
				cas_id = str(int(time.time() * 10000))
				Cases.objects.create(id=cas_id, name=name, description=desc, project_id=project_id, created_by=user_name, updated_by=user_name, create_time=time_strftime(), update_time=time_strftime())
				logger.info(f'{user_name}---{name}用例创建成功')
				return JsonResponse({'code': 0, 'msg': '用例创建成功', 'data': None})
		else:
			logger.error('用例名称不能为空')
			return JsonResponse({'code': 1, 'msg': '用例名称不能为空', 'data': None})
	if request.method == 'GET':
		project_id = request.GET.get('projectId')
		user_name = request.user.username
		return render(request, 'ATI/cases/add.html', context={'username': user_name, 'project_id': project_id})


def edit_case(request):
	"""
	编辑用例
	"""
	if request.method == 'POST':
		case_id = request.POST.get('Id')
		project_id = request.POST.get('project_id')
		name = request.POST.get('name')
		user_name = request.user.username
		r = Cases.objects.get(id=case_id, project_id=project_id)
		r.name = name
		r.description = request.POST.get('description')
		r.update_time = time_strftime()
		r.updated_by = user_name
		r.save()
		logger.info(f'{user_name}---变量{name}修改成功')
		return JsonResponse({'code': 0, 'msg': '变量修改成功', 'data': None})

	if request.method == 'GET':
		user_name = request.user.username
		project_id = request.GET.get('projectId')
		case_id = request.GET.get('Id')
		project_name = Projects.objects.get(id=project_id, type='ATI').name
		cases = Cases.objects.get(id=case_id, project_id=project_id)
		return render(request, 'ATI/variable/edit.html', context={'username': user_name, 'cases': cases, 'project_name': project_name , 'project_id': project_id})


def delete_case(request):
	"""
	删除用例
	"""
	if request.method == "GET":
		case_id = request.GET.get('Id')
		project_id = request.GET.get('projectId')
		user_name = request.user.username
		try:
			Cases.objects.get(project_id=project_id, id=case_id).delete()
			logger.info(f'{user_name}---{case_id}变量删除成功')
		except Exception as err:
			logger.error(err)
		return HttpResponseRedirect(f'/ATI/case?projectId={project_id}')


def show_case_interface(request):
	"""
		查看用例中的接口
	"""
	case_id = request.GET.get('Id')
	project_id = request.GET.get('projectId')
	page_num = request.GET.get('pageNum')
	if page_num:
		page_num = int(page_num)
	else:
		page_num = 1

	user_name = request.user.username
	start_index = (page_num - 1) * 10
	end_index = page_num * 10
	total_num = InterfaceCase.objects.filter(case_id=case_id).count()
	case_interfaces = InterfaceCase.objects.filter(case_id=case_id).order_by('display_sort')[start_index:end_index]
	return render(request, 'ATI/cases/interfaces.html', context={'username': user_name, 'project_id': project_id, 'case_id': case_id, 'case_interfaces': case_interfaces, 'page_num': page_num, 'total_num': math.ceil(total_num / 10)})


def add_case_interface(request):
	"""
	给用例增加接口，查看接口列表
	"""
	if request.method == 'GET':
		project_id = request.GET.get('projectId')
		case_id = request.GET.get('caseId')
		page_num = request.GET.get('pageNum')
		content = request.GET.get('Content')
		if page_num:
			page_num = int(page_num)
		else:
			page_num = 1

		user_name = request.user.username
		start_index = (page_num - 1) * 10
		end_index = page_num * 10

		project_name = Projects.objects.get(type='ATI', id=project_id).name

		if content:
			total_num = Interfaces.objects.filter(Q(project_id=project_id), Q(name__contains=content) | Q(interface__contains=content)).count()
			interface_list = Interfaces.objects.filter(Q(project_id=project_id), Q(name__contains=content) | Q(interface__contains=content)).order_by('-update_time')[start_index:end_index]
		else:
			total_num = Interfaces.objects.filter(project_id=project_id).count()
			interface_list = Interfaces.objects.filter(project_id=project_id).order_by('-update_time')[start_index:end_index]

		return render(request, 'ATI/cases/add_interface.html', context={'username': user_name, 'interface_list': interface_list, 'project_name': project_name, 'project_id': project_id, 'case_id': case_id, 'page_num': page_num, 'total_num': math.ceil(total_num / 10)})


def add_interface_to_case(request):
	"""
	给用例增加接口
	"""
	try:
		user_name = request.user.username
		case_id = request.POST.get('caseId')
		interface_id = request.POST.get('interfaceId')
		total_num = InterfaceCase.objects.filter(case_id=case_id).count()
		InterfaceCase.objects.create(case_id=case_id, interface_id=interface_id, is_run=1, display_sort=total_num+1)
		logger.info(f'{user_name}---将接口{interface_id}添加到用例{case_id}中')
		return JsonResponse({'code': 0, 'msg': '接口添加成功', 'data': None})
	except Exception as err:
		logger.error(err)
		logger.error(traceback.format_exc())
		return JsonResponse({'code': 1, 'msg': '接口添加异常', 'data': None})


def set_is_run(request):
	"""
	设置是否执行
	"""
	try:
		user_name = request.user.username
		case_id = request.POST.get('caseId')
		interface_id = request.POST.get('interfaceId')
		is_run = request.POST.get('isRun')
		if case_id:
			r = Cases.objects.get(id=case_id)
			r.is_run = is_run
			r.save()
			logger.info(f'{user_name}----{case_id}是否执行设置为{is_run}')
		if interface_id:
			r = InterfaceCase.objects.get(id=interface_id)
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
		case_id = request.POST.get('caseId')
		interface_id = request.POST.get('interfaceId')
		is_up = request.POST.get('is_up')
		if is_up == '0':
			current_sort = InterfaceCase.objects.get(case_id=case_id, interface_id=interface_id).display_sort
			downer = InterfaceCase.objects.filter(case_id=case_id, display_sort__gt=current_sort).order_by('display_sort').first().id
			r = InterfaceCase.objects.get(case_id=case_id, interface_id=interface_id)
			r.display_sort = current_sort + 1
			r.save()

			r = InterfaceCase.objects.get(id=downer)
			r.display_sort = current_sort
			r.save()

			logger.info(f'{user_name}---用例{case_id}向下移动成功')

		else:
			current_sort = InterfaceCase.objects.get(case_id=case_id, interface_id=interface_id).display_sort
			upper = InterfaceCase.objects.filter(case_id=case_id, display_sort__lt=current_sort).order_by('display_sort').last().id
			r = InterfaceCase.objects.get(case_id=case_id, interface_id=interface_id)
			r.display_sort = current_sort - 1
			r.save()

			r = InterfaceCase.objects.get(id=upper)
			r.display_sort = current_sort
			r.save()

			logger.info(f'{user_name}---用例{case_id}向上移动成功')

		return JsonResponse({'code': 0, 'msg': '移动成功', 'data': None})

	except AttributeError as err:
		logger.error(err)
		return JsonResponse({'code': 0, 'msg': '移动成功', 'data': None})

	except Exception as err:
		logger.error(err)
		logger.error(traceback.format_exc())
		return JsonResponse({'code': 1, 'msg': '移动失败', 'data': None})


def edit_interface_from_case(request):
	"""
	编辑接口
	"""
	if request.method == 'POST':
		interface_id = request.POST.get('interface_id')
		project_id = request.POST.get('project_id')
		user_name = request.user.username
		r = Interfaces.objects.get(id=interface_id, project_id=project_id)
		r.name = request.POST.get('name')
		r.interface = request.POST.get('interface')
		r.protocol = request.POST.get('protocol')
		r.method = request.POST.get('method')
		r.parameter = request.POST.get('parameter')
		r.timeout = request.POST.get('timeout') if request.POST.get('timeout') else 500
		r.header = request.POST.get('header')
		r.pre_process = request.POST.get('pre_process')
		r.post_process = request.POST.get('post_process')
		r.except_result = request.POST.get('except_result')
		r.assert_method = request.POST.get('assert_method')
		r.assert_result = request.POST.get('assert_result')
		r.description = request.POST.get('description')
		r.updated_by = user_name
		r.update_time = time_strftime()
		r.save()
		logger.info(f'{user_name}---{interface_id}接口修改成功')
		return JsonResponse({'code': 0, 'msg': '接口修改成功', 'data': None})

	if request.method == 'GET':
		interface_id = request.GET.get('Id')
		project_id = request.GET.get('projectId')
		case_id = request.GET.get('caseId')
		user_name = request.user.username
		interface = Interfaces.objects.get(id=interface_id, project_id=project_id)
		return render(request, 'ATI/cases/edit_interface.html', context={'interface': interface, 'username': user_name, 'project_id': project_id, 'case_id': case_id})


def delete_interface_from_case(request):
	"""
	从用例中删除接口
	"""
	user_name = request.user.username
	ID = request.GET.get('Id')
	case_id = request.GET.get('caseId')
	interface_id = request.GET.get('interfaceId')
	project_id = request.GET.get('projectId')
	try:
		InterfaceCase.objects.get(id=ID, interface_id=interface_id).delete()
		logger.info(f'{user_name}---接口{case_id}从用例{interface_id}中删除')
		# return JsonResponse({'code': 0, 'msg': '删除成功', 'data': None})
	except Exception as err:
		logger.error(err)
		# return JsonResponse({'code': 1, 'msg': '删除失败', 'data': None})
	return HttpResponseRedirect(f'/ATI/case/interface?Id={case_id}&projectId={project_id}')


def variables(request):
	"""
		查询当前用户下所有的全局变量
		:param request:
		:return:
	"""
	if request.method == 'GET':
		project_id = request.GET.get('projectId')
		page_num = request.GET.get('pageNum')
		if page_num:
			page_num = int(page_num)
		else:
			page_num = 1

		user_name = request.user.username
		start_index = (page_num - 1) * 10
		end_index = page_num * 10

		project_ids = UserProject.objects.filter(type='ATI', user_name=user_name).values('project_id')
		projects = Projects.objects.filter(type='ATI', id__in=project_ids).values_list('id', 'name')
		p_dict = {}
		for pro in projects:
			p_dict.update({str(pro[0]): pro[1]})

		if project_id:
			total_num = Variables.objects.filter(project_id=project_id).count()
			global_list = Variables.objects.filter(project_id=project_id).order_by('-update_time')[start_index:end_index]
		else:
			project_id = ''
			total_num = Variables.objects.filter(project_id__in=project_ids).count()
			global_list = Variables.objects.filter(project_id__in=project_ids).order_by('-update_time')[start_index:end_index]

		return render(request, 'ATI/variable/index.html', context={'username': user_name, 'global_list': global_list, 'projects': p_dict, 'project_list': projects, 'project_id': project_id, 'page_num': page_num, 'total_num': math.ceil(total_num / 10)})


def add_variable(request):
	"""
		添加变量
		"""
	if request.method == 'POST':
		name = request.POST.get('name')
		project_id = request.POST.get('project_id')
		user_name = request.user.username
		if name:
			if Variables.objects.filter(name=name, project_id=project_id):
				logger.warning('变量已存在，请勿重复添加')
				return JsonResponse({'code': 1, 'msg': '变量已存在，请勿重复添加！', 'data': None})
			else:
				value_v = request.POST.get('value')
				desc = request.POST.get('description')
				Variables.objects.create(name=name, description=desc, value=value_v, project_id=project_id, create_time=time_strftime(),
										created_by=user_name, updated_by=user_name, update_time=time_strftime())
				logger.info(f'{user_name}---{name}变量创建成功')
				return JsonResponse({'code': 0, 'msg': '变量创建成功', 'data': None})
		else:
			logger.error('变量名称不能为空')
			return JsonResponse({'code': 1, 'msg': '变量名称不能为空', 'data': None})
	if request.method == 'GET':
		user_name = request.user.username
		project_ids = UserProject.objects.filter(type='ATI', user_name=user_name).values('project_id')
		projects = Projects.objects.filter(type='ATI', id__in=project_ids).values_list('id', 'name')
		return render(request, 'ATI/variable/add.html', context={'project_list': projects})


def edit_variable(request):
	"""
		编辑变量
	"""
	if request.method == 'POST':
		name = request.POST.get('name')
		project_id = request.POST.get('project_id')
		user_name = request.user.username
		r = Variables.objects.get(name=name, project_id=project_id)
		r.value = request.POST.get('value')
		r.description = request.POST.get('description')
		r.update_time = time_strftime()
		r.updated_by = user_name
		r.save()
		logger.info(f'{user_name}---变量{name}修改成功')
		return JsonResponse({'code': 0, 'msg': '变量修改成功', 'data': None})

	if request.method == 'GET':
		name = request.GET.get('name')
		project_id = request.GET.get('projectId')
		project_name = Projects.objects.get(id=project_id, type='ATI').name
		variables = Variables.objects.get(name=name, project_id=project_id)
		return render(request, 'ATI/variable/edit.html', context={'variables': variables, 'project_name': project_name})


def delete_variable(request):
	"""
		删除变量
	"""
	if request.method == "GET":
		name = request.GET.get('name')
		project_id = request.GET.get('projectId')
		user_name = request.user.username
		try:
			Variables.objects.get(project_id=project_id, name=name).delete()
			logger.info(f'{user_name}---{name}变量删除成功')
		except Exception as err:
			logger.error(err)
		return HttpResponseRedirect(f'/ATI/variable?projectId={project_id}')


def plans(request):
	"""
	测试计划
	"""
	if request.method == 'GET':
		project_id = request.GET.get('projectId')
		page_num = request.GET.get('pageNum')
		content = request.GET.get('Content')
		if page_num:
			page_num = int(page_num)
		else:
			page_num = 1

		user_name = request.user.username
		start_index = (page_num - 1) * 10
		end_index = page_num * 10

		project_name = Projects.objects.get(type='ATI', id=project_id).name

		if content:
			total_num = Plans.objects.filter(Q(project_id=project_id), Q(name__contains=content)).count()
			plan_list = Plans.objects.filter(Q(project_id=project_id), Q(name__contains=content)).order_by('-update_time')[start_index:end_index]
		else:
			total_num = Plans.objects.filter(project_id=project_id).count()
			plan_list = Plans.objects.filter(project_id=project_id).order_by('-update_time')[start_index:end_index]

		return render(request, 'ATI/plan/index.html', context={'username': user_name, 'plan_list': plan_list, 'project_name': project_name, 'project_id': project_id, 'page_num': page_num, 'total_num': math.ceil(total_num / 10)})


def add_plan(request):
	"""
	添加测试计划
	"""
	if request.method == 'POST':
		name = request.POST.get('name')
		project_id = request.POST.get('project_id')
		user_name = request.user.username
		if name:
			if Cases.objects.filter(name=name, project_id=project_id):
				logger.warning('用例已存在，请勿重复添加')
				return JsonResponse({'code': 1, 'msg': '用例已存在，请勿重复添加！', 'data': None})
			else:
				desc = request.POST.get('description')
				cas_id = str(int(time.time() * 10000))
				Cases.objects.create(id=cas_id, name=name, description=desc, project_id=project_id, created_by=user_name, updated_by=user_name, create_time=time_strftime(), update_time=time_strftime())
				logger.info(f'{user_name}---{name}用例创建成功')
				return JsonResponse({'code': 0, 'msg': '用例创建成功', 'data': None})
		else:
			logger.error('用例名称不能为空')
			return JsonResponse({'code': 1, 'msg': '用例名称不能为空', 'data': None})
	if request.method == 'GET':
		project_id = request.GET.get('projectId')
		user_name = request.user.username
		return render(request, 'ATI/plan/add.html', context={'username': user_name, 'project_id': project_id})
