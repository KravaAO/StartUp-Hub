from django.urls import path
from . import views

app_name = 'workspace'

urlpatterns = [
    path('<int:project_id>/', views.board_view, name='board'),
]