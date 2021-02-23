import json
from . import models
from spider.settings import VERSION, EXCEL_PATH
from urllib.request import quote
from django.shortcuts import render
from common.views.common import login_required
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse, FileResponse
from datetime import datetime


@login_required
@csrf_protect
def html(request):
    return render(request, 'spider/html/export.html', {"VERSION": VERSION})


# ajax api
@csrf_protect
def show_data(request):
    username = request.session['username']
    id = request.POST['id']
    begin_date = request.POST['begin_date']
    end_date = request.POST['end_date']
    dict_ = {'username': username, 'id': id, 'begin_date': begin_date, 'end_date': end_date}
    data = models.to_html(dict_)
    return HttpResponse(json.dumps(data), content_type='application/json; charset=utf-8')


@csrf_protect
def download_data(request):
    username = request.session['username']
    ids = request.GET['id'].split(',')
    begin_date = request.GET['begin_date']
    end_date = request.GET['end_date']
    file_list = []
    for id in ids:
        _dict = {'username': username, 'id': id, 'begin_date': begin_date, 'end_date': end_date}
        filename = models.to_excel(_dict)
        file_list.append(filename)
    if len(file_list) == 1:
        filename = file_list[0]
    else:
        filename = '{}_{}-{}.zip'.format(datetime.now().strftime('%Y%m%d%H%M%S'), begin_date[0:10].replace('-', ''), end_date[0:10].replace('-', ''))
        models.zip_excels(file_list, filename)
    file = open(EXCEL_PATH + filename, 'rb')
    user_agent = request.META.get('HTTP_USER_AGENT')
    if 'Gecko' in user_agent:
        filename = quote(filename)
    else:
        filename = filename.encode('utf-8').decode('ISO-8859-1')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{}"'.format(filename)
    return response
