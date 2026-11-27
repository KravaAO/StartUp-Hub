
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from projects.models import Project, ProjectRole
from teams.models import Application


@override_settings(ROOT_URLCONF="teams.urls")
class ApplicationViewTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(
            username="owner_test", password="test-pass-123"
        )
        self.user = User.objects.create_user(
            username="candidate_test", password="test-pass-123"
        )
        self.project = Project.objects.create(
            owner=self.owner,
            title="Demo",
            short_description="Demo project",
            description="Testing",
            status=Project.Status.RECRUITING,
            is_public=True,
        )
        self.role = ProjectRole.objects.create(
            project=self.project,
            title="Backend Developer",
            description="Python",
            slots=2,
        )
        self.url = f"/roles/{self.role.pk}/apply/"

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_application_created(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.url, {"message": "Хочу до команди"}
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Application.objects.filter(
                applicant=self.user,
                project_role=self.role,
                status=Application.Status.PENDING,
            ).exists()
        )

    def test_duplicate_application_rejected(self):
        self.client.force_login(self.user)
        self.client.post(self.url, {"message": "Перша"})
        response = self.client.post(
            self.url, {"message": "Друга"}
        )
        self.assertEqual(response.status_code, 409)

    def test_closed_role_rejected(self):
        self.role.is_open = False
        self.role.save()
        self.client.force_login(self.user)
        response = self.client.post(
            self.url, {"message": "Хочу до команди"}
        )
        self.assertEqual(response.status_code, 404)

    def test_application_form_renders(self):
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "teams/application_form.html"
        )
