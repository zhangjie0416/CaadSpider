from django.urls import path

from help import views

# api
urlpatterns = [
    path('login', views.login),
    path('change_password/', views.change_password),
    path('create_user/', views.create_user),
    path('logout/', views.logout),
    path('get_versions', views.get_versions),
    path('new_version', views.new_version),
    path('is_read', views.is_read),
]
