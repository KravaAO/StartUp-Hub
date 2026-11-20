from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
from projects.models import Project
from .models import Task


@login_required
def board_view(request, project_id):
  project = get_object_or_404(Project, id=project_id)


  if project.owner != request.user:
    raise PermissionDenied('У вас немає доступу до робочого простору цього проєкту.')


  tasks = Task.objects.filter(project=project).select_related('assignee', 'created_by')


  context = {
      'project': project,
      'planned_tasks': tasks.filter(status=Task.Status.PLANNED),
      'in_progress_tasks': tasks.filter(status=Task.Status.IN_PROGRESS),
      'done_tasks': tasks.filter(status=Task.Status.DONE),
  }

  return render(request, 'workspace/board.html', context)