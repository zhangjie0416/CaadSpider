"""Spider URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from help import views as help
from spider_example import views as spider_example
from spider_export import views as spider_export
from spider_running import views as spider_running
from spider_setting import views as spider_setting

urlpatterns = [
    # login/logout
    path('', help.login, name='CaadSpider-登陆'),
    path('login.html', help.login, name='CaadSpider-登陆'),

    # html
    path('spider/example.html', spider_example.html, name='采集-模版'),
    path('spider/setting.html', spider_setting.html, name='采集-配置'),
    path('spider/running.html', spider_running.html, name='采集-运行'),
    path('spider/export.html', spider_export.html, name='采集-导出'),

    path('help.html', help.html, name='帮助-帮助'),

    # api
    path('spider/example/', include('spider_example.urls'), name="采集-模版-api接口"),
    path('spider/setting/', include('spider_setting.urls'), name="采集-配置-api接口"),
    path('spider/running/', include('spider_running.urls'), name="采集-运行-api接口"),
    path('spider/export/', include('spider_export.urls'), name="采集-导出-api接口"),

    path('help/', include('help.urls'), name="help-api接口"),

    # admin
    path('admin.html', admin.site.urls),
]
