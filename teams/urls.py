
from django.urls import path
from . import views

app_name = "teams"

urlpatterns = [
    path(
        "roles/<int:role_id>/apply/",
        views.apply_to_role,
        name="apply"
    ),

    path(
        "projects/<int:project_id>/applications/",
        views.application_list,
        name="applications"
    ),

    path(
        "applications/<int:application_id>/approve/",
        views.approve_application,
        name="approve"
    ),

    path(
        "applications/<int:application_id>/reject/",
        views.reject_application,
        name="reject"
    ),
]
