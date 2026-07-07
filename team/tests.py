from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AuthFlowTests(TestCase):
    def test_login_page_renders_login_form(self):
        response = self.client.get(reverse('team:login'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Log In')
        self.assertContains(response, 'name="egn"')
        self.assertContains(response, 'name="password"')

    def test_registration_creates_pending_user(self):
        response = self.client.post(
            reverse('team:register'),
            {
                'role': 'child',
                'full_name': 'Test User',
                'egn': '1234567890',
                'email': 'test@example.com',
                'password': 'secret123',
                'date_of_birth': '2000-01-01',
            },
        )

        self.assertRedirects(response, reverse('team:login'))
        user = get_user_model().objects.get(egn='1234567890')
        self.assertFalse(user.is_approved)
        self.assertTrue(user.check_password('secret123'))

    def test_unapproved_user_cannot_login(self):
        user = get_user_model().objects.create_user(
            egn='0987654321',
            full_name='Pending User',
            email='pending@example.com',
            password='secret123',
            is_approved=False,
        )

        response = self.client.post(
            reverse('team:login'),
            {'egn': '0987654321', 'password': 'secret123'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'pending approval')
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertTrue(get_user_model().objects.filter(pk=user.pk).exists())
