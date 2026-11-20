from django.test import TestCase

# Create your tests here.

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from projects.models import Project, ProjectRole
from teams.models import Application, TeamMembership


User = get_user_model()


class TeamModelsTests(TestCase):

    def setUp(self):
        self.owner = User.objects.create_user(username="owner")
        self.applicant = User.objects.create_user(username="applicant")

        self.project = Project.objects.create(
            owner=self.owner,
            title="Test Project",
            short_description="Test description",
            description="Project for testing"
        )

        self.role = ProjectRole.objects.create(
            project=self.project,
            title="Backend Developer",
            description="Python developer"
        )

    def test_application_default_status(self):
        application = Application.objects.create(
            project_role=self.role,
            applicant=self.applicant
        )

        self.assertEqual(application.status, "pending")

    def test_duplicate_pending_application(self):
        Application.objects.create(
            project_role=self.role,
            applicant=self.applicant
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Application.objects.create(
                    project_role=self.role,
                    applicant=self.applicant
                )

    def test_rejected_application_allows_new_pending(self):
        Application.objects.create(
            project_role=self.role,
            applicant=self.applicant,
            status=Application.Status.REJECTED
        )

        new_application = Application.objects.create(
            project_role=self.role,
            applicant=self.applicant
        )

        self.assertEqual(new_application.status, "pending")

    def test_membership_creation(self):
        membership = TeamMembership.objects.create(
            project=self.project,
            user=self.applicant,
            role="Backend Developer"
        )

        self.assertEqual(membership.role, "Backend Developer")
        self.assertEqual(membership.project, self.project)
        self.assertEqual(membership.user, self.applicant)

    def test_duplicate_membership(self):
        TeamMembership.objects.create(
            project=self.project,
            user=self.applicant,
            role="Backend Developer"
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                TeamMembership.objects.create(
                    project=self.project,
                    user=self.applicant,
                    role="Designer"
                )
