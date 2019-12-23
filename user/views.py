from django.shortcuts import render

# Create your views here.

from django.shortcuts import render_to_response
from django.http import JsonResponse


def index(request):
	return render_to_response('index.html')


def home(request):
	return render_to_response('home.html')


def login(request):
	if request.method == 'POST':
		if request.POST:
			username = request.POST.get('username')
			password = request.POST.get('password')
			return JsonResponse({'code': 0, 'msg': '操作成功', 'data': {'username': username, 'userid': 'aaaa'}})
		else:
			return JsonResponse({'code': 1, 'msg': '传参为空', 'data': None})
	else:
		return JsonResponse({'code': 1, 'msg': '参数异常', 'data': None})


def regist(request):
	if request.method == 'POST':
		if request.POST:
			username = request.POST.get('username')
			password = request.POST.get('password')
			return JsonResponse({'code': 0, 'msg': '操作成功', 'data': {'username': username, 'userid': 'aaaa'}})
		else:
			return JsonResponse({'code': 1, 'msg': '传参为空', 'data': None})
	else:
		return JsonResponse({'code': 1, 'msg': '参数异常', 'data': None})
