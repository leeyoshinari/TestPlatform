import math
from django.shortcuts import render, HttpResponseRedirect
from django.http import JsonResponse
from django.views.decorators.clickjacking import xframe_options_sameorigin
from .models import Project
from common.timeFormat import time_strftime


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
		username = request.COOKIES.get('userName')
		start_index = (page_num - 1) * 1
		end_index = page_num * 10
		total_num = Project.objects.filter(pro_type='ATI', username__contains=username).count()
		print(total_num)
		projects = Project.objects.filter(pro_type='ATI', username__contains=username).order_by('-update_time')[start_index:end_index]
		print(projects)
		return render(request, 'ATI/project/index.html', context={'projects': projects, 'page_num': page_num, 'total_num': math.ceil(total_num/10)})


def add_project(request):
	if request.method == 'POST':
		code = request.POST.get('code')
		if code:
			if Project.objects.filter(code=code):
				return JsonResponse({'code': 1, 'msg': '项目编码已存在', 'data': None})
			else:
				name = request.POST.get('name')
				username = request.COOKIES.get('userName')
				desc = request.POST.get('description')
				Project.objects.create(name=name, code=code, description=desc, pro_type='ATI',
				                       create_time=time_strftime(), update_time=time_strftime(), username=username)
				return JsonResponse({'code': 0, 'msg': '项目创建成功', 'data': None})

		else:
			return JsonResponse({'code': 1, 'msg': '项目编码不能为空', 'data': None})
	if request.method == 'GET':
		return render(request, 'ATI/project/add.html')


def update_project(request):
	if request.method == 'POST':
		r = Project.objects.get(code=request.POST.get('code'))
		r.name = request.POST.get('name')
		r.description = request.POST.get('description')
		r.update_time = time_strftime()
		r.save()
		return JsonResponse({'code': 0, 'msg': '项目保存成功', 'data': None})

	if request.method == 'GET':
		code = request.GET.get('code')
		projects = Project.objects.get(code=code)
		return render(request, 'ATI/project/update.html', context={'projects': projects})


def del_project(request):
	if request.method == "GET":
		code = request.GET.get('code')
		Project.objects.get(code=code).delete()
		return HttpResponseRedirect('/ATI/project/')


def manager_project(request):
	if request.method == 'GET':
		code = request.GET.get('code')
		projects = Project.objects.get(code=code)
		return render(request, 'ATI/project/manager.html', context={'projects': projects})

	if request.method == 'POST':
		username = request.POST.get('username')
		r = Project.objects.get(code=request.POST.get('code'))
		if request.POST.get('isadd') == '0':
			usernames = r.username.strip().split(',')
			if username in usernames:
				usernames.pop(usernames.index(username))
				r.username = ','.join(usernames) + ','
				r.save()
				return JsonResponse({'code': 0, 'msg': '删除成功', 'data': None})
			else:
				return JsonResponse({'code': 1, 'msg': '该用户不在项目中', 'data': None})

		if request.POST.get('isadd') == '1':
			usernames = r.username.strip().split(',')
			if username in usernames:
				return JsonResponse({'code': 1, 'msg': '该用户已在项目中', 'data': None})
			else:
				usernames.append(username)
				r.username = ','.join(usernames) + ','
				r.save()
				return JsonResponse({'code': 0, 'msg': '添加成功', 'data': None})


def variables(request):
	return render(request, 'ATI/variable/index.html')


def add_variable(request):
	return render(request, 'ATI/variable/add.html')
