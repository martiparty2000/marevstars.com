from django.test import TestCase
from django.urls import reverse


class PublicAuthAndPaymentRemovalTests(TestCase):
    def test_public_login_register_logout_and_payment_routes_are_removed(self):
        for route_name in ['team:login', 'team:register', 'team:logout', 'team:payment']:
            with self.assertRaisesMessage(Exception, 'Reverse for'):
                reverse(route_name)

        self.assertEqual(self.client.get('/login/').status_code, 404)
        self.assertEqual(self.client.get('/register/').status_code, 404)
        self.assertEqual(self.client.get('/logout/').status_code, 404)
        self.assertEqual(self.client.get('/payment/').status_code, 404)
