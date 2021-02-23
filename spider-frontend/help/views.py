from . import models
from spider.settings import VERSION
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from common.views.common import login_required
import json


@login_required
@csrf_protect
def html(request):
    return render(request, 'default/html/help.html', {"username": request.session['username'], "VERSION": VERSION})


# 登录
@csrf_protect
def login(request):
    username = request.GET.get('username')
    password = request.GET.get('password')
    if request.session.get('islogin', False) and request.session.get('username', False):
        response = redirect('/spider/setting.html')
    elif username and password:
        dict_ = {'username': username, 'password': password}
        user = models.login_check(dict_)
        if user:
            request.session['islogin'] = True
            request.session['user_id'] = user[0]['id']
            request.session['username'] = user[0]['username']
            response = JsonResponse({'success': 1})
            request.session.set_expiry(60 * 60 * 24)
            response.set_cookie('username', username, max_age=60 * 60 * 24)
            response.set_cookie('is_read', 0)
    elif request.session.get('username'):
        username = request.session.get('username')
        response = render(request, 'default/html/login.html', {'username': username})
    else:
        response = render(request, 'default/html/login.html')
    return response


# 退出
@csrf_protect
def logout(request):
    request.session['islogin'] = False
    return JsonResponse({'success': 1})


# 修改密码
@csrf_protect
def change_password(request):
    username = request.POST['username']
    password = request.POST['password']
    dict_ = {'username': username, 'password': password}
    if models.update_user(dict_):
        request.session['islogin'] = False
        return JsonResponse({'success': 1})


@csrf_protect
def create_user(request):
    username = request.POST['username']
    password = request.POST['password']
    company = request.POST['company']
    dict_ = {'username': username, 'password': password, 'company': company}
    if models.insert_user(dict_):
        return JsonResponse({'success': 1})


@csrf_protect
def get_versions(request):
    username = request.GET.get('username', None)
    version = request.GET.get('version', None)
    _dict = {'username': username, 'version': version}
    versions = models.select_versions(_dict)
    return HttpResponse(json.dumps(versions, ensure_ascii=False), content_type='application/json; charset=utf-8')


def new_version(request):
    bool = models.update_session()
    return HttpResponse(bool, content_type='application/json; charset=utf-8')


def is_read(request):
    username = request.GET['username']
    _dict = {'username': username}
    _is_read = models.select_read(_dict)[0]
    return HttpResponse(json.dumps(_is_read, ensure_ascii=False), content_type='application/json; charset=utf-8')
