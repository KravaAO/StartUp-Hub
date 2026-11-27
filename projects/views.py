from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProjectForm
from .models import Category, Project


def project_list(request):
    """Public catalog: only is_public=True, search by title, filter by status/category."""
    projects = (
        Project.objects.filter(is_public=True)
        .select_related('category', 'owner')
        .prefetch_related('roles')
    )

    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    category = request.GET.get('category', '')

    if q:
        projects = projects.filter(title__icontains=q)
    if status in Project.Status.values:
        projects = projects.filter(status=status)
    if category.isdigit():
        projects = projects.filter(category_id=int(category))

    return render(request, 'projects/project_list.html', {
        'projects': projects,
        'categories': Category.objects.all(),
        'statuses': Project.Status.choices,
        'q': q,
        'selected_status': status,
        'selected_category': category,
    })


def project_detail(request, pk):
    """Public projects are visible to everyone; drafts only to their owner."""
    project = get_object_or_404(
        Project.objects.select_related('category', 'owner').prefetch_related('roles'),
        pk=pk,
    )
    is_owner = request.user.is_authenticated and project.owner_id == request.user.id
    if not project.is_public and not is_owner:
        raise Http404

    return render(request, 'projects/project_detail.html', {
        'project': project,
        'roles': project.roles.all(),
        'is_owner': is_owner,
    })


@login_required
def project_create(request):
    form = ProjectForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user  # status=draft, is_public=False are model defaults
        project.save()
        messages.success(request, 'Чернетку створено. Додайте ролі та опублікуйте проєкт.')
        return redirect('projects:detail', pk=project.pk)
    return render(request, 'projects/project_form.html', {'form': form, 'is_edit': False})


@login_required
def project_edit(request, pk):
    # Not the owner -> 404 (we don't reveal that the project exists)
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Зміни збережено.')
        return redirect('projects:detail', pk=project.pk)
    return render(request, 'projects/project_form.html', {
        'form': form, 'project': project, 'is_edit': True,
    })


@login_required
@require_POST
def project_publish(request, pk):
    """Publish = is_public=True + status=recruiting. Requires at least one open role."""
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if not project.roles.filter(is_open=True).exists():
        messages.error(request, 'Щоб опублікувати проєкт, додайте хоча б одну відкриту роль.')
        return redirect('projects:detail', pk=project.pk)

    project.is_public = True
    project.status = Project.Status.RECRUITING
    project.save(update_fields=['is_public', 'status'])
    messages.success(request, 'Проєкт опубліковано.')
    return redirect('projects:detail', pk=project.pk)
