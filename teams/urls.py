
from django.urls import path
from . import views

app_name = "teams"

urlpatterns = [
    path(
        "roles/<int:role_id>/apply/",
        views.apply_to_role,
        name="apply"
    ),
]
