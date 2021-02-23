import json
from . import models
from django.shortcuts import render
from spider.settings import VERSION
from spider_running.views import get_fields
from common.views.common import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect


# page
@login_required
@csrf_protect
def html(request):
    # 返回：example页面
    return render(request, 'spider/html/example.html', {"VERSION": VERSION})


# ajax api
@csrf_protect
def get_details(request):
    # 返回：一条example详情
    id = request.POST["id"]
    fields = get_fields(id)
    return HttpResponse(json.dumps(fields), content_type='application/json; charset=utf-8')


@csrf_protect
def delete_example(request):
    # 返回：删除一条example
    id = request.POST["id"]
    dict = {'id': id}
    if models.delete_example(dict):
        return JsonResponse({"success": 1})


@csrf_protect
def get_examples_user(request):
    user_id = request.session.get("user_id")
    dict = {'user_id': user_id}
    data_list = models.select_examples(dict)
    return HttpResponse(json.dumps(data_list), content_type='application/json; charset=utf-8')


@csrf_protect
def get_examples_all(request):
    data_list = models.select_examples()
    return HttpResponse(json.dumps(data_list), content_type='application/json; charset=utf-8')
