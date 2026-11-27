from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render

from projects.models import Project, ProjectRole
from .forms import ApplicationForm
from .models import Application, TeamMembership


@login_required
def apply_to_role(request, role_id):
    role = get_object_or_404(
        ProjectRole.objects.select_related("project"),
        pk=role_id
    )

    # Only public projects recruiting for an open role
    if (
        not role.is_open
        or not role.project.is_public
        or role.project.status != Project.Status.RECRUITING
    ):
        raise Http404("Позиція недоступна")

    # Project owner cannot apply to their own project
    if role.project.owner_id == request.user.pk:
        return HttpResponse(
            "Власник не може подати заявку",
            status=403
        )

    # User is already a member
    if TeamMembership.objects.filter(
        project=role.project,
        user=request.user
    ).exists():
        return HttpResponse(
            "Ви вже учасник цього проєкту",
            status=409
        )

    # Prevent duplicate pending applications
    if Application.objects.filter(
        project_role=role,
        applicant=request.user,
        status=Application.Status.PENDING
    ).exists():
        return HttpResponse(
            "Ви вже подали заявку на цю позицію",
            status=409
        )

    if request.method == "POST":
        form = ApplicationForm(request.POST)

        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = request.user
            application.project_role = role

            try:
                with transaction.atomic():
                    application.save()
            except IntegrityError:
                return HttpResponse(
                    "Заявка вже існує",
                    status=409
                )

            return HttpResponse(
                "Заявку успішно надіслано!",
                status=201
            )
    else:
        form = ApplicationForm()

    return render(
        request,
        "teams/application_form.html",
        {"form": form, "role": role}
    )
