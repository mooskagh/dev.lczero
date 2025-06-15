from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

# Testing imports for future use
# from .models import Artifact, Revision, Target

User = get_user_model()


class ArtifactsViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")

    def test_artifacts_table_view_renders_without_errors(self):
        """Test that artifacts table view renders without URL reverse errors"""
        response = self.client.get(reverse("artifacts:table"))
        self.assertEqual(response.status_code, 200)

    def test_artifacts_table_view_with_admin_user(self):
        """Test that admin users can access table with management features"""
        self.user.is_staff = True
        self.user.save()
        self.client.force_login(self.user)

        response = self.client.get(reverse("artifacts:table"))
        self.assertEqual(response.status_code, 200)
        # Should not crash on missing admin URLs if user has permissions
