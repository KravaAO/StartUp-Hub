from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Project(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        RECRUITING = 'recruiting', 'Recruiting'
        ACTIVE = 'active', 'Active'
        ARCHIVED = 'archived', 'Archived'

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_projects')
    title = models.CharField(max_length=200)
    short_description = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    deadline = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects',
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def open_roles(self):
        return [r for r in self.roles.all() if r.is_open]

    @property
    def open_slots(self):
        return sum(r.slots for r in self.open_roles)


class ProjectRole(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='roles')
    title = models.CharField(max_length=200)
    description = models.TextField()
    is_open = models.BooleanField(default=True)
    slots = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title