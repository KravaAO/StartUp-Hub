from django.urls import path

from . import views, views_roles

app_name = 'projects'

urlpatterns = [
    path('', views.project_list, name='list'),
    path('new/', views.project_create, name='create'),
    path('<int:pk>/', views.project_detail, name='detail'),
    path('<int:pk>/edit/', views.project_edit, name='edit'),
    path('<int:pk>/publish/', views.project_publish, name='publish'),
    path('<int:project_id>/roles/new/', views_roles.role_create, name='role_create'),
    path('roles/<int:role_id>/edit/', views_roles.role_edit, name='role_edit'),
    path('roles/<int:role_id>/close/', views_roles.role_close, name='role_close'),
]
