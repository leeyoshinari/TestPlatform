import uuid
from django.shortcuts import render, HttpResponseRedirect

# Create your views here.

from django.http import JsonResponse
from .models import UserModel
from common.timeFormat import time_strftime


def home(request):
	return render(request, 'user/home.html')


def login(request):
	"""
	登录
	:param request:
	:return:
	"""
	if request.method == 'POST':
		if request.POST:
			username = request.POST.get('username')
			password = request.POST.get('password')

			try:
				user_info = UserModel.objects.get(username=username, password=password)
				user_id = uuid.uuid1()  # 随机生成uuid，用于cookie验证
				user_info.user_id = user_id
				user_info.last_login_time = time_strftime()
				user_info.save()

				response = JsonResponse({'code': 0, 'msg': '登录成功！', 'data': {'username': username, 'userid': user_id}})
				response.set_cookie('userName', username, max_age=7200)  # 设置cookie
				response.set_cookie('userId', user_id, max_age=7200)

				return response
			except Exception as err:
				return JsonResponse({'code': 1, 'msg': '用户名或密码错误', 'data': None})
		else:
			return JsonResponse({'code': 1, 'msg': '参数异常', 'data': None})
	else:
		return render(request, 'user/login.html')


def sign(request):
	"""
	注册用户
	:param request:
	:return:
	"""
	if request.method == 'POST':
		if request.POST:
			username = request.POST.get('username')
			password = request.POST.get('password')

			if UserModel.objects.filter(username=username):
				return JsonResponse({'code': 1, 'msg': '用户已存在，请登录', 'data': None})
			else:
				UserModel.objects.create(username=username, password=password, create_time=time_strftime(),
										 user_id='', last_login_time=time_strftime())
				return JsonResponse({'code': 0, 'msg': '注册成功', 'data': {'username': username}})
		else:
			return JsonResponse({'code': 1, 'msg': '参数异常', 'data': None})
	else:
		return render(request, 'user/sign.html')


def logout(request):
	return None
