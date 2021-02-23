import re
import json
import requests
import itertools
from . import models
from urllib import parse
from django.shortcuts import render
from django.http import HttpResponse
from common.views.common import login_required
from django.views.decorators.csrf import csrf_protect
from spider.settings import VERSION, SQL_API, DOWMLOAD_API, PARSER_API


@login_required
@csrf_protect
def html(request):
    return render(request, 'spider/html/setting.html', {"VERSION": VERSION})


@login_required
def get_setting(request):
    id = request.GET.get('id')
    dict = {'id': id}
    setting = models.select_setting(dict)[0]
    return HttpResponse(json.dumps(setting, ensure_ascii=False), content_type='application/json; charset=utf-8')


# 生成一级网址
@csrf_protect
def get_first_urls(request):
    url = request.POST['url']
    first_urls = generate_first_urls(url)
    data_list, max_length, length = [], 10, len(first_urls)
    pages = length // max_length - 1
    if length > max_length:
        data_list.append('......省略')
        for i in range(0, max_length):
            data_list.append(first_urls[i * pages + i])
        data_list.append('......省略')
    else:
        data_list = first_urls
    data_list.insert(0, '共{}条网址'.format(length))
    return HttpResponse(json.dumps(data_list), content_type='application/json; charset=utf-8')


# 二级网址测试
@csrf_protect
def get_urls(request):
    # 返回网页源码中的所有二级网址
    url = parse.quote(request.POST['url'])
    xpath = request.POST['xpath']
    xpath = xpath.replace("('", '("').replace("','", '","').replace("')", '")')
    postdata = {'url': url, 'xpath': xpath, 'type': 'frontend'}
    try:
        html = requests.post(url=PARSER_API, data=json.dumps(postdata), timeout=8).text
        urls = json.loads(html)
        urls.insert(0, '共{}条网址'.format(len(urls)))
        return HttpResponse(json.dumps(urls), content_type='application/json; charset=utf-8')
    except:
        return HttpResponse("error", content_type='application/json; charset=utf-8')


# 获取fields
@csrf_protect
def get_fields(request):
    # 返回网页源码中的所有采集字段
    url = parse.quote(request.POST['url'])
    xpath = request.POST['xpath']
    xpath = xpath.replace("('", '("').replace("','", '","').replace("')", '")')
    postdata = {'url': url, 'xpath': xpath, 'type': 'frontend'}
    try:
        html = requests.post(url=PARSER_API, data=json.dumps(postdata), timeout=8).text
        fields = json.loads(html)
        return HttpResponse(json.dumps(fields), content_type='application/json; charset=utf-8')
    except:
        return HttpResponse("error", content_type='application/json; charset=utf-8')


# 获取html
@csrf_protect
def get_html(request):
    # 返回网页源码
    url = parse.quote(request.POST['url'])
    html = requests.get(url='{}?url={}'.format(DOWMLOAD_API, url)).text
    return HttpResponse(html, content_type='application/text; charset=utf-8')


# 上传html
@csrf_protect
def save_html(request):
    url = request.POST['url']
    html = request.POST['html']
    bool = requests.post(url=SQL_API, data=json.dumps({'url': url, 'html': html}), timeout=8).text
    return HttpResponse(bool, content_type='application/text; charset=utf-8')


# 保存
@csrf_protect
def save_setting(request):
    # 保存setting界面的信息，并作校验，如果存在则更新这条信息
    user_id = request.session.get('user_id')
    setting = request.POST['setting']
    dict = json.loads(setting)
    dict['user_id'] = user_id
    result = models.update_setting(dict)
    return HttpResponse('保存成功！{}'.format(result), content_type='application/json; charset=utf-8')


# 另存
@csrf_protect
def save_as_setting(request):
    # 保存setting界面的信息，并作校验，如果存在则更新这条信息
    user_id = request.session.get('user_id')
    setting = request.POST['setting']
    dict = json.loads(setting)
    dict['user_id'] = user_id
    result = models.insert_setting(dict)
    return HttpResponse('保存成功！{}'.format(result), content_type='application/json; charset=utf-8')


def generate_first_urls(_first_urls):
    urls = []
    try:
        first_urls_list = json.loads(_first_urls)
    except:
        first_urls_list = [_first_urls]
    for first_urls in first_urls_list:
        items = re.findall('{.*?}', first_urls)
        if items:
            args = []
            for item in items:
                if re.findall('-', item):
                    interval = re.findall(r'\d+', item)
                    args.append([i for i in range(int(interval[0]), int(interval[1]) + 1)])
                else:
                    args.append(item[1:-1].split(','))
            for i in itertools.product(*args):
                urls.append(re.sub('{.*?}', '{}', first_urls).format(*i))
        else:
            urls.append(first_urls)
    return urls
