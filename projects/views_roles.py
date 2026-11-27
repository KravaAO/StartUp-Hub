from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms_roles import ProjectRoleForm
from .models import Project, ProjectRole


def _check_project_owner(project, user):
    if project.owner != user:
        raise PermissionDenied('Тільки власник проєкту може керувати ролями.')


@login_required
def role_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    _check_project_owner(project, request.user)

    if request.method == 'POST':
        form = ProjectRoleForm(request.POST)
        if form.is_valid():
            role = form.save(commit=False)
            role.project = project
            role.save()
            return redirect('projects:detail', pk=project.pk)
    else:
        form = ProjectRoleForm()

    return render(
        request,
        'projects/role_form.html',
        {'form': form, 'project': project, 'is_edit': False},
    )


@login_required
def role_edit(request, role_id):
    role = get_object_or_404(ProjectRole.objects.select_related('project'), pk=role_id)
    _check_project_owner(role.project, request.user)

    if request.method == 'POST':
        form = ProjectRoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            return redirect('projects:detail', pk=role.project.pk)
    else:
        form = ProjectRoleForm(instance=role)

    return render(
        request,
        'projects/role_form.html',
        {'form': form, 'project': role.project, 'role': role, 'is_edit': True},
    )


@login_required
@require_POST
def role_close(request, role_id):
    role = get_object_or_404(ProjectRole.objects.select_related('project'), pk=role_id)
    if role.project.owner != request.user:
        raise Http404('Роль або проєкт не знайдено.')

    role.is_open = False
    role.save(update_fields=['is_open'])
    return redirect('projects:detail', pk=role.project.pk)