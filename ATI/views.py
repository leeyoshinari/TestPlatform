import math
import time
import logging
from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.clickjacking import xframe_options_sameorigin
from user.models import Projects, UserProject
from ATI.models import Variables
from common.timeFormat import time_strftime


logger = logging.getLogger('django')


def home(request):
	return render(request, 'ATI/home.html')


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
		return render(request, 'ATI/project/index.html', context={'projects': projects, 'page_num': page_num, 'total_num': math.ceil(total_num/10)})


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

		return render(request, 'ATI/variable/index.html', context={'global_list': global_list, 'projects': p_dict, 'project_list': projects, 'project_id': str(project_id), 'page_num': page_num, 'total_num': math.ceil(total_num / 10)})


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
		user_name = request.user.username
		try:
			name = request.GET.get('name')
			project_id = request.GET.get('projectId')
			Variables.objects.get(project_id=project_id, name=name).delete()
			logger.info(f'{user_name}---{name}变量删除成功')
		except Exception as err:
			logger.error(err)
		return HttpResponseRedirect(f'/ATI/variable?projectId={project_id}')
