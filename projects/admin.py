from django.contrib import admin

from .models import Project, ProjectRole


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    exclude = ('budget',)


admin.site.register(ProjectRole)
