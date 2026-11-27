from django.urls import path

from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_list, name='list'),
    path('new/', views.project_create, name='create'),
    path('<int:pk>/', views.project_detail, name='detail'),
    path('<int:pk>/edit/', views.project_edit, name='edit'),
    path('<int:pk>/publish/', views.project_publish, name='publish'),
    # TODO (after Georgiy's PR is merged): role routes
    # path('<int:project_pk>/roles/new/', views_roles.role_create, name='role_create'),
    # path('roles/<int:pk>/edit/', views_roles.role_edit, name='role_edit'),
    # path('roles/<int:pk>/close/', views_roles.role_close, name='role_close'),
]
