from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import TestCase, override_settings
from django.urls import include, path, reverse

from . import views_roles
from .forms_roles import ProjectRoleForm
from .models import Project, ProjectRole

User = get_user_model()


def dummy_project_detail(request, pk):
    return HttpResponse(f'Project {pk}')


projects_patterns = [
    path('<int:pk>/', dummy_project_detail, name='detail'),
    path('<int:project_id>/roles/create/', views_roles.role_create, name='role_create'),
    path('roles/<int:role_id>/edit/', views_roles.role_edit, name='role_edit'),
    path('roles/<int:role_id>/close/', views_roles.role_close, name='role_close'),
]

urlpatterns = [
    path('projects/', include((projects_patterns, 'projects'), namespace='projects')),
]


@override_settings(ROOT_URLCONF=__name__)
class ProjectRoleTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='password123')
        self.other_user = User.objects.create_user(username='other', password='password123')
        self.project = Project.objects.create(
            owner=self.owner,
            title='StartUp Idea',
            short_description='Short desc',
            description='Full description',
        )
        self.role = ProjectRole.objects.create(
            project=self.project,
            title='Backend Developer',
            description='Python / Django',
            slots=2,
            is_open=True,
        )

    def test_form_rejects_slots_less_than_one(self):
        form_zero = ProjectRoleForm(data={
            'title': 'Frontend',
            'description': 'UI',
            'slots': 0,
            'is_open': True,
        })
        self.assertFalse(form_zero.is_valid())
        self.assertIn('slots', form_zero.errors)

        form_valid = ProjectRoleForm(data={
            'title': 'Frontend',
            'description': 'UI',
            'slots': 1,
            'is_open': True,
        })
        self.assertTrue(form_valid.is_valid())

    def test_owner_can_create_edit_and_close_role(self):
        self.client.force_login(self.owner)

        create_url = reverse('projects:role_create', kwargs={'project_id': self.project.pk})
        resp_create = self.client.post(create_url, {
            'title': 'Designer',
            'description': 'Figma',
            'slots': 1,
            'is_open': True,
        })
        self.assertEqual(resp_create.status_code, 302)
        self.assertEqual(resp_create['Location'], reverse('projects:detail', kwargs={'pk': self.project.pk}))
        self.assertTrue(ProjectRole.objects.filter(project=self.project, title='Designer').exists())

        edit_url = reverse('projects:role_edit', kwargs={'role_id': self.role.pk})
        resp_edit = self.client.post(edit_url, {
            'title': 'Senior Backend',
            'description': 'Django + PostgreSQL',
            'slots': 3,
            'is_open': True,
        })
        self.assertEqual(resp_edit.status_code, 302)
        self.assertEqual(resp_edit['Location'], reverse('projects:detail', kwargs={'pk': self.project.pk}))
        self.role.refresh_from_db()
        self.assertEqual(self.role.title, 'Senior Backend')
        self.assertEqual(self.role.slots, 3)

        close_url = reverse('projects:role_close', kwargs={'role_id': self.role.pk})
        resp_close = self.client.post(close_url)
        self.assertEqual(resp_close.status_code, 302)
        self.assertEqual(resp_close['Location'], reverse('projects:detail', kwargs={'pk': self.project.pk}))
        self.role.refresh_from_db()
        self.assertFalse(self.role.is_open)

    def test_non_owner_cannot_create_edit_or_close_role(self):
        self.client.force_login(self.other_user)

        resp_create = self.client.post(
            reverse('projects:role_create', kwargs={'project_id': self.project.pk}),
            {'title': 'Hacker Role', 'description': 'Test', 'slots': 1, 'is_open': True},
        )
        self.assertEqual(resp_create.status_code, 403)

        resp_edit = self.client.post(
            reverse('projects:role_edit', kwargs={'role_id': self.role.pk}),
            {'title': 'Changed', 'description': 'Test', 'slots': 1, 'is_open': True},
        )
        self.assertEqual(resp_edit.status_code, 403)

        resp_close = self.client.post(reverse('projects:role_close', kwargs={'role_id': self.role.pk}))
        self.assertEqual(resp_close.status_code, 404)
        self.role.refresh_from_db()
        self.assertTrue(self.role.is_open)