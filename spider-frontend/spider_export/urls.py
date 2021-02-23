from django.urls import path

from spider_export import views

urlpatterns = [
    path('show_data/', views.show_data),
    path('download_data/', views.download_data),
]
