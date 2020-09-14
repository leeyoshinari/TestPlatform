import logging
from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import JsonResponse


logger = logging.getLogger('django')


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
            if 'HTTP_X_FORWARDED_FOR' in request.META:
                ip = request.META['HTTP_X_FORWARDED_FOR']
            else:
                ip = request.META['REMOTE_ADDR']

            logger.info(f'用户{username}，客户端IP为{ip}')
            session = auth.authenticate(username=username, password=password)
            if session:
                auth.login(request, session)
                request.session.set_expiry(7200)    # 设置session过期时间，单位秒
                response = JsonResponse({'code': 0, 'msg': f'{username}登录成功！', 'data': None})
                # response.set_cookie('userName', username, max_age=7200)  # 设置cookie
                logger.info(f'{username}登录成功！')

                return response
            else:
                logger.error(f'{username}用户名或密码错误')
                return JsonResponse({'code': 1, 'msg': '用户名或密码错误', 'data': None})
        else:
            return JsonResponse({'code': 1, 'msg': '参数异常', 'data': None})
    else:
        return render(request, 'user/login.html')


'''def sign(request):
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
        return render(request, 'user/sign.html')'''


def logout(request):
    auth.logout(request)
    logger.info(f"{request.user.username}登出成功！")
    return redirect('/')


def changePwd(request):
    if request.method == 'POST':
        old_pwd = request.POST.get('old_pwd')
        if request.user.check_password(old_pwd):
            new_pwd = request.POST.get('new_pwd')
            request.user.set_password(new_pwd)
            request.user.save()
            return JsonResponse({'code': 0, 'msg': '密码修改成功', 'data': None})
    else:
        return render(request, 'user/sign.html')


def userInfo(request):
    pass
