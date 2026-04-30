from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Role, UserProfile
from .views import is_admin


class AdminAccessTests(TestCase):
    def setUp(self):
        self.admin_role, _ = Role.objects.get_or_create(name='admin')
        self.client_role, _ = Role.objects.get_or_create(name='client')

        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            email='admin@example.com',
            is_active=True,
        )
        UserProfile.objects.create(
            user=self.admin_user,
            role=self.admin_role,
            phone='0000000000',
        )

        self.client_user = User.objects.create_user(
            username='client_user',
            password='test1234',
            email='client@example.com',
            is_active=True,
        )
        UserProfile.objects.create(
            user=self.client_user,
            role=self.client_role,
            phone='1111111111',
        )

    def test_is_admin_returns_true_only_for_admin_user(self):
        self.assertTrue(is_admin(self.admin_user))
        self.assertFalse(is_admin(self.client_user))

    def test_dashboard_admin_visible_to_admin(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('dashboard_admin'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_admin_forbidden_for_non_admin(self):
        self.client.force_login(self.client_user)
        response = self.client.get(reverse('dashboard_admin'))
        self.assertEqual(response.status_code, 403)
