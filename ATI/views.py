import datetime
from django.shortcuts import render, HttpResponseRedirect
from django.http import JsonResponse
from django.views.decorators.clickjacking import xframe_options_sameorigin
from .models import Project


def home(request):
	return render(request, 'ATI/home.html')


def project(request):
	username = request.COOKIES.get('userName')
	projects = Project.objects.filter(pro_type='ATI', username__contains=',' + username + ',')
	return render(request, 'ATI/project/index.html', context={'projects': projects})


@xframe_options_sameorigin
def add_project(request):
	if request.method == 'POST':
		code = request.POST['code']
		if code:
			if Project.objects.filter(code=code):
				return JsonResponse({'code': 1, 'msg': '项目编码已存在', 'data': None})
			else:
				name = request.POST['name']
				username = request.COOKIES.get('userName')
				desc = request.POST['description']
				Project.objects.create(name=name, code=code, description=desc, pro_type='ATI',
				                       create_time=datetime.datetime.now(), username=',' + username + ',')
				return JsonResponse({'code': 0, 'msg': '项目创建成功', 'data': None})

		else:
			return JsonResponse({'code': 1, 'msg': '项目编码不能为空', 'data': None})
	if request.method == 'GET':
		return render(request, 'ATI/project/add.html')


@xframe_options_sameorigin
def update_project(request):
	if request.method == 'POST':
		r = Project.objects.get(code=request.POST['code'])
		r.name = request.POST['name']
		r.description = request.POST['description']
		r.save()
		return JsonResponse({'code': 0, 'msg': '项目保存成功', 'data': None})

	if request.method == 'GET':
		code = request.GET['code']
		projects = Project.objects.get(code=code)
		return render(request, 'ATI/project/update.html', context={'projects': projects})


def del_project(request):
	if request.method == "GET":
		code = request.GET['code']
		Project.objects.get(code=code).delete()
		return HttpResponseRedirect('/ATI/project/')


def manager_project(request):
	if request.method == 'GET':
		code = request.GET['code']
		projects = Project.objects.get(code=code)
		return render(request, 'ATI/project/manager.html', context={'projects': projects})

	if request.method == 'POST':
		username = request.POST['username']
		r = Project.objects.get(code=request.POST['code'])
		if request.POST['isadd'] == '0':
			usernames = r.username.strip().split(',')
			if username in usernames:
				usernames.pop(usernames.index(username))
				r.username = ','.join(usernames) + ','
				r.save()
				return JsonResponse({'code': 0, 'msg': '删除成功', 'data': None})
			else:
				return JsonResponse({'code': 1, 'msg': '该用户不在项目中', 'data': None})

		if request.POST['isadd'] == '1':
			usernames = r.username.strip().split(',')
			if username in usernames:
				return JsonResponse({'code': 1, 'msg': '该用户已在项目中', 'data': None})
			else:
				usernames.append(username)
				r.username = ','.join(usernames) + ','
				r.save()
				return JsonResponse({'code': 0, 'msg': '添加成功', 'data': None})
