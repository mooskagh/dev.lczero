"""Tests for menu system."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from lczero_dev_portal.menu import get_menu_for_user

User = get_user_model()


class MenuTestCase(TestCase):
    """Test cases for menu system."""

    def test_anonymous_user_sees_public_menus(self):
        """Anonymous users should see menus with permissions=None."""
        user = AnonymousUser()
        menu = get_menu_for_user(user)

        # Should see Home and Artifacts groups
        self.assertEqual(len(menu), 2)
        self.assertEqual(menu[0].title, "Home")
        self.assertEqual(menu[1].title, "Artifacts")

    def test_authenticated_user_sees_all_menus(self):
        """Authenticated users should see all menus."""
        user = User.objects.create(username="testuser")
        menu = get_menu_for_user(user)

        # Should see Home and Artifacts groups
        self.assertEqual(len(menu), 2)
        self.assertEqual(menu[0].title, "Home")
        self.assertEqual(menu[1].title, "Artifacts")
