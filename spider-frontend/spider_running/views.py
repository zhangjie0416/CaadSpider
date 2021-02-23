import json
from datetime import datetime
from . import models
from spider.settings import VERSION
from django.shortcuts import render
from common.views.common import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect


# page
@login_required
@csrf_protect
def html(request):
    # 返回显示模板页面信息
    return render(request, 'spider/html/running.html', {"VERSION": VERSION})


# ajax api
@csrf_protect
def get_start_list(request):
    user_id = request.session.get('user_id')
    username = request.session.get('username')
    from_date = request.POST['from_date']
    dict_ = {'user_id': user_id, 'username': username, 'data_status': 1, 'from_date': from_date}
    data_list = models.select_runnings(dict_)
    return HttpResponse(json.dumps(data_list, ensure_ascii=False), content_type='application/json; charset=utf-8')


@csrf_protect
def get_stop_list(request):
    user_id = request.session.get('user_id')
    username = request.session.get('username')
    from_date = request.POST['from_date']
    dict_ = {'user_id': user_id, 'username': username, 'data_status': 0, 'from_date': from_date}
    data_list = models.select_runnings(dict_)
    return HttpResponse(json.dumps(data_list, ensure_ascii=False), content_type='application/json; charset=utf-8')


@csrf_protect
def get_details(request):
    # 返回：一条example详情
    id = request.POST['id']
    fields = get_fields(id)
    return HttpResponse(json.dumps(fields), content_type='application/json; charset=utf-8')


def get_fields(id):
    dict_ = {'id': id}
    fields = models.select_details(dict_)
    return fields


@csrf_protect
def start_running(request):
    # 开始 {开始:1}
    status = request.POST['status']
    id = request.POST['id']
    _dict = {'id': id, 'status': status}
    if models.update_running(_dict):  # 更新spider_setting表
        return JsonResponse({"success": 0})


@csrf_protect
def stop_running(request):
    # 结束 {结束:0}
    status = request.POST['status']
    id = request.POST['id']
    _dict = {'id': id, 'status': status}
    if models.update_running(_dict):
        return JsonResponse({"success": 0})


@csrf_protect
def delete_running(request):
    # 删除
    id = request.POST['id']
    dict_ = {'id': int(id)}
    if models.delete_running(dict_):
        return JsonResponse({"success": 0})


def update_timers(request):
    # 批量定时
    id = request.POST['id']
    timer = request.POST['timer']
    _dict = {'id': id, 'timer': timer}
    if models.update_setting_timer(_dict):
        return JsonResponse({"success": 0})
