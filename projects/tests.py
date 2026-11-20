from django.contrib.auth import get_user_model
from django.test import TestCase
from .models import Project, ProjectRole

User = get_user_model()


class ProjectAndRoleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="georgii_test",
            password="password123",
        )

    def test_new_project_is_draft_and_not_public(self):
        project = Project.objects.create(
            owner=self.user,
            title="Нова ідея",
            short_description="Короткий опис",
            description="Повний опис",
        )
        self.assertEqual(project.status, Project.Status.DRAFT)
        self.assertFalse(project.is_public)

    def test_project_roles_via_related_name(self):
        project = Project.objects.create(
            owner=self.user,
            title="Проєкт із ролями",
            short_description="Короткий опис",
            description="Повний опис",
        )
        role_1 = ProjectRole.objects.create(
            project=project,
            title="Backend",
            description="Серверна частина",
        )
        role_2 = ProjectRole.objects.create(
            project=project,
            title="Frontend",
            description="Інтерфейс",
        )

        roles = project.roles.all()
        self.assertEqual(roles.count(), 2)
        self.assertIn(role_1, roles)
        self.assertIn(role_2, roles)

    def test_role_defaults_open_and_one_slot(self):
        project = Project.objects.create(
            owner=self.user,
            title="Перевірка ролі",
            short_description="Короткий опис",
            description="Повний опис",
        )
        role = ProjectRole.objects.create(
            project=project,
            title="Designer",
            description="Дизайн",
        )
        self.assertTrue(role.is_open)
        self.assertEqual(role.slots, 1)

    def test_deleting_project_deletes_its_roles(self):
        project = Project.objects.create(
            owner=self.user,
            title="Видалення проєкту",
            short_description="Короткий опис",
            description="Повний опис",
        )
        role = ProjectRole.objects.create(
            project=project,
            title="QA",
            description="Тестування",
        )
        project.delete()
        self.assertFalse(ProjectRole.objects.filter(pk=role.pk).exists())