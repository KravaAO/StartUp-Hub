from django.contrib import admin
from .models import Project, ProjectRole


class ProjectRoleInline(admin.TabularInline):
    model = ProjectRole
    extra = 1
    verbose_name = "Роль у проєкті"
    verbose_name_plural = "Ролі у проєкті"


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "status", "is_public", "created_at")
    list_filter = ("status", "is_public")
    search_fields = ("title",)
    exclude = ("budget",)
    inlines = [ProjectRoleInline]


@admin.register(ProjectRole)
class ProjectRoleAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "is_open", "slots")
    list_filter = ("is_open",)
    search_fields = ("title", "project__title")