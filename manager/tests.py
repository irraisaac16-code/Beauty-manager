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


class AdminTestLoginBehaviorTests(TestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.admin_dashboard_url = reverse('dashboard_admin')

    def test_admin_test_login_creates_admin_account_and_redirects(self):
        self.assertFalse(User.objects.filter(username='admin_test').exists())

        response = self.client.post(
            self.login_url,
            {'username': 'admin_test', 'password': 'AdminTest123!'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.admin_dashboard_url)
        admin_test_user = User.objects.get(username='admin_test')
        self.assertTrue(admin_test_user.is_active)
        self.assertTrue(admin_test_user.is_staff)
        self.assertTrue(admin_test_user.is_superuser)
        self.assertEqual(admin_test_user.userprofile.role.name, 'admin')

    def test_admin_test_login_accepts_password_with_surrounding_whitespace(self):
        response = self.client.post(
            self.login_url,
            {'username': 'admin_test', 'password': ' AdminTest123! '},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.admin_dashboard_url)

    def test_admin_test_login_resynchronizes_admin_privileges(self):
        client_role, _ = Role.objects.get_or_create(name='client')
        user = User.objects.create_user(
            username='admin_test',
            password='AdminTest123!',
            email='admin_test@example.com',
            is_active=False,
            is_staff=False,
            is_superuser=False,
        )
        UserProfile.objects.create(user=user, role=client_role, phone='1234567890')

        response = self.client.post(
            self.login_url,
            {'username': 'admin_test', 'password': 'AdminTest123!'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.admin_dashboard_url)
        user.refresh_from_db()
        user.userprofile.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.userprofile.role.name, 'admin')
