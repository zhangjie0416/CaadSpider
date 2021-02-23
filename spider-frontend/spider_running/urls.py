from django.urls import path

from spider_running import views

urlpatterns = [
    path('get_start_list/', views.get_start_list),
    path('get_stop_list/', views.get_stop_list),
    path('get_details/', views.get_details),
    path('start_running/', views.start_running),
    path('stop_running/', views.stop_running),
    path('delete_running/', views.delete_running),
    path('update_timers/', views.update_timers),
]
