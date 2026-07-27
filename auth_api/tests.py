from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class LocalAuthFallbackTests(TestCase):
    def test_register_and_login_without_external_api(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "localuser",
                "email": "local@example.com",
                "password": "strongpass123",
                "password_confirm": "strongpass123",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(get_user_model().objects.filter(username="localuser").exists())

        login_response = self.client.post(
            reverse("login"),
            {"email": "local@example.com", "password": "strongpass123"},
        )

        self.assertEqual(login_response.status_code, 302)
        self.assertIn("access_token", self.client.session)
