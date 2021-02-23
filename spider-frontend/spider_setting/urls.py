from django.urls import path

from spider_setting import views

# ajax api
urlpatterns = [
    path('get_setting/', views.get_setting),
    path('get_first_urls/', views.get_first_urls),
    path('get_urls/', views.get_urls),
    path('get_html/', views.get_html),
    path('get_fields/', views.get_fields),
    path('save_html/', views.save_html),
    path('save_setting/', views.save_setting),
    path('save_as_setting/', views.save_as_setting),
]
