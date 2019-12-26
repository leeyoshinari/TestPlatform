from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse


def login(request):
	return render(request, 'login.html')


def signin(request):
	return render(request, 'signin.html')


def home(request):
	return render(request, 'home.html')


def log_in(request):
	if request.method == 'POST':
		if request.POST:
			username = request.POST.get('username')
			password = request.POST.get('password')
			return JsonResponse({'code': 0, 'msg': '操作成功', 'data': {'username': username, 'userid': 'aaaa'}})
		else:
			return JsonResponse({'code': 1, 'msg': '传参为空', 'data': None})
	else:
		return JsonResponse({'code': 1, 'msg': '请求异常', 'data': None})


def sign_in(request):
	if request.method == 'POST':
		if request.POST:
			username = request.POST.get('username')
			password = request.POST.get('password')
			return JsonResponse({'code': 0, 'msg': '操作成功', 'data': {'username': username}})
		else:
			return JsonResponse({'code': 1, 'msg': '传参为空', 'data': None})
	else:
		return JsonResponse({'code': 1, 'msg': '请求异常', 'data': None})


def logout(request):
	if request.method == 'POST':
		if request.POST:
			username = request.POST.get('username')
			userid = request.POST.get('password')
			return JsonResponse({'code': 0, 'msg': '操作成功', 'data': {'username': username}})
		else:
			return JsonResponse({'code': 1, 'msg': '传参为空', 'data': None})
	else:
		return JsonResponse({'code': 1, 'msg': '请求异常', 'data': None})