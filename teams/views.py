from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render

from projects.models import Project, ProjectRole
from .forms import ApplicationForm
from .models import Application, TeamMembership

from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

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


@login_required
def application_list(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if project.owner_id != request.user.pk:
        return HttpResponseForbidden(
            "Лише власник може переглядати заявки."
        )

    applications = (
        Application.objects
        .filter(project_role__project=project)
        .select_related("applicant", "project_role")
        .order_by("-created_at")
    )

    return render(
        request,
        "teams/application_list.html",
        {
            "project": project,
            "applications": applications,
        }
    )


@login_required
@require_POST
def approve_application(request, application_id):
    try:
        with transaction.atomic():
            application = get_object_or_404(
                Application.objects
                .select_related("project_role__project")
                .select_for_update(),
                pk=application_id
            )

            role = ProjectRole.objects.select_for_update().get(
                pk=application.project_role_id
            )
            project = application.project_role.project

            # Only the project owner may approve
            if project.owner_id != request.user.pk:
                return HttpResponseForbidden(
                    "Лише власник може схвалювати заявки."
                )

            if application.status != Application.Status.PENDING:
                return HttpResponse(
                    "Заявку вже розглянуто.",
                    status=409
                )

            if not role.is_open:
                return HttpResponse(
                    "Позицію закрито.",
                    status=409
                )

            # Prevent duplicate membership
            if TeamMembership.objects.filter(
                project=project,
                user=application.applicant
            ).exists():
                return HttpResponse(
                    "Користувач уже в команді.",
                    status=409
                )

            # Check available positions
            occupied = TeamMembership.objects.filter(
                project_role=role
            ).count()

            if occupied >= role.slots:
                return HttpResponse(
                    "Вільних місць більше немає.",
                    status=409
                )

            TeamMembership.objects.create(
                project=project,
                project_role=role,
                user=application.applicant,
                role=role.title
            )

            application.status = Application.Status.APPROVED
            application.save(update_fields=["status"])

    except IntegrityError:
        return HttpResponse(
            "Не вдалося додати учасника.",
            status=409
        )

    return redirect(
        "teams:applications",
        project_id=project.pk
    )


@login_required
@require_POST
def reject_application(request, application_id):
    with transaction.atomic():
        application = get_object_or_404(
            Application.objects
            .select_related("project_role__project")
            .select_for_update(),
            pk=application_id
        )

        project = application.project_role.project

        if project.owner_id != request.user.pk:
            return HttpResponseForbidden(
                "Лише власник може відхиляти заявки."
            )

        if application.status != Application.Status.PENDING:
            return HttpResponse(
                "Заявку вже розглянуто.",
                status=409
            )

        application.status = Application.Status.REJECTED
        application.save(update_fields=["status"])

    return redirect(
        "teams:applications",
        project_id=project.pk
    )
