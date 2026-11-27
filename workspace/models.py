from django.conf import settings
from django.db import models


class Task(models.Model):

  class Status(models.TextChoices):
    PLANNED = 'planned', 'Planned'
    IN_PROGRESS = 'in_progress', 'In Progress'
    DONE = 'done', 'Done'

  project = models.ForeignKey(
      'projects.Project',
      on_delete=models.CASCADE,
      related_name='tasks',
      verbose_name='Проєкт',
  )
  title = models.CharField(max_length=255, verbose_name='Назва задачі')
  description = models.TextField(blank=True, verbose_name='Опис')
  status = models.CharField(
      max_length=20,
      choices=Status.choices,
      default=Status.PLANNED,
      verbose_name='Статус',
  )
  deadline = models.DateField(null=True, blank=True, verbose_name='Дедлайн')
  assignee = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.SET_NULL,
      null=True,
      blank=True,
      related_name='assigned_tasks',
      verbose_name='Виконавець',
  )
  created_by = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE,
      related_name='created_tasks',
      verbose_name='Автор',
  )
  created_at = models.DateTimeField(
      auto_now_add=True, verbose_name='Дата створення'
  )

  def __str__(self):
    return self.title

  class Meta:
    verbose_name = 'Задача'
    verbose_name_plural = 'Задачі'