
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from projects.models import Project, ProjectRole
from teams.models import Application
from teams.models import Application, TeamMembership

@override_settings(ROOT_URLCONF="teams.test_urls")
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

@override_settings(ROOT_URLCONF="teams.test_urls")
class ApplicationDecisionTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.owner = User.objects.create_user(
            username="decision_owner",
            password="test-pass-123"
        )
        self.candidate = User.objects.create_user(
            username="decision_candidate",
            password="test-pass-123"
        )
        self.outsider = User.objects.create_user(
            username="decision_outsider",
            password="test-pass-123"
        )

        self.project = Project.objects.create(
            owner=self.owner,
            title="Test Project",
            short_description="Test",
            description="Test project",
            status=Project.Status.RECRUITING,
            is_public=True,
        )

        self.role = ProjectRole.objects.create(
            project=self.project,
            title="Backend Developer",
            description="Django",
            slots=1
        )

        self.application = Application.objects.create(
            project_role=self.role,
            applicant=self.candidate,
            message="Хочу до команди"
        )

        self.list_url = (
            f"/projects/{self.project.pk}/applications/"
        )
        self.approve_url = (
            f"/applications/{self.application.pk}/approve/"
        )
        self.reject_url = (
            f"/applications/{self.application.pk}/reject/"
        )

    def test_owner_can_view_applications(self):
        self.client.force_login(self.owner)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "decision_candidate")

    def test_approve_creates_membership(self):
        self.client.force_login(self.owner)

        response = self.client.post(self.approve_url)

        self.assertEqual(response.status_code, 302)

        self.application.refresh_from_db()

        self.assertEqual(
            self.application.status,
            Application.Status.APPROVED
        )

        membership = TeamMembership.objects.get(
            project=self.project,
            user=self.candidate
        )

        self.assertEqual(membership.project_role, self.role)
        self.assertEqual(membership.role, "Backend Developer")

    def test_reject_application(self):
        self.client.force_login(self.owner)

        response = self.client.post(self.reject_url)

        self.assertEqual(response.status_code, 302)

        self.application.refresh_from_db()

        self.assertEqual(
            self.application.status,
            Application.Status.REJECTED
        )

        self.assertFalse(
            TeamMembership.objects.filter(
                user=self.candidate,
                project=self.project
            ).exists()
        )

    def test_outsider_cannot_manage_applications(self):
        self.client.force_login(self.outsider)

        self.assertEqual(
            self.client.get(self.list_url).status_code,
            403
        )
        self.assertEqual(
            self.client.post(self.approve_url).status_code,
            403
        )
        self.assertEqual(
            self.client.post(self.reject_url).status_code,
            403
        )

        self.application.refresh_from_db()
        self.assertEqual(
            self.application.status,
            Application.Status.PENDING
        )

    def test_cannot_exceed_slots(self):
        User = get_user_model()
        existing_member = User.objects.create_user(
            username="existing_member"
        )

        TeamMembership.objects.create(
            project=self.project,
            user=existing_member,
            project_role=self.role,
            role="Backend Developer"
        )

        self.client.force_login(self.owner)

        response = self.client.post(self.approve_url)

        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            TeamMembership.objects.filter(
                project_role=self.role
            ).count(),
            1
        )

    def test_approve_only_accepts_post(self):
        self.client.force_login(self.owner)

        self.assertEqual(
            self.client.get(self.approve_url).status_code,
            405
        )
        self.assertEqual(
            self.client.get(self.reject_url).status_code,
            405
        )

    def test_cannot_approve_twice(self):
        self.client.force_login(self.owner)

        first = self.client.post(self.approve_url)
        second = self.client.post(self.approve_url)

        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 409)
        self.assertEqual(
            TeamMembership.objects.filter(
                project=self.project,
                user=self.candidate
            ).count(),
            1
        )


    def test_anonymous_cannot_manage_applications(self):
        response_list = self.client.get(self.list_url)
        response_approve = self.client.post(self.approve_url)
        response_reject = self.client.post(self.reject_url)

        self.assertEqual(response_list.status_code, 302)
        self.assertEqual(response_approve.status_code, 302)
        self.assertEqual(response_reject.status_code, 302)

        self.application.refresh_from_db()
        self.assertEqual(
            self.application.status,
            Application.Status.PENDING
        )

    def test_closed_role_cannot_be_approved(self):
        self.role.is_open = False
        self.role.save()

        self.client.force_login(self.owner)
        response = self.client.post(self.approve_url)

        self.assertEqual(response.status_code, 409)

        self.application.refresh_from_db()
        self.assertEqual(
            self.application.status,
            Application.Status.PENDING
        )

        self.assertFalse(
            TeamMembership.objects.filter(
                project=self.project,
                user=self.candidate
            ).exists()
        )

    def test_rejected_application_cannot_be_approved(self):
        self.application.status = Application.Status.REJECTED
        self.application.save(update_fields=["status"])

        self.client.force_login(self.owner)
        response = self.client.post(self.approve_url)

        self.assertEqual(response.status_code, 409)

        self.assertFalse(
            TeamMembership.objects.filter(
                project=self.project,
                user=self.candidate
            ).exists()
        )
