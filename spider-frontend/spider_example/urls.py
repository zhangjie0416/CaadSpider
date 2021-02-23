from django.urls import path

from spider_example import views

urlpatterns = [
    path('get_examples_user/', views.get_examples_user),
    path('get_examples_all/', views.get_examples_all),
    path('get_details/', views.get_details),
    path('delete_example/', views.delete_example),
]
