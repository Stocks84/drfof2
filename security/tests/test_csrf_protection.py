from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

class CSRFProtectionTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.register_url = reverse('register')
        cls.admin_login_url = reverse('admin:login')

    def test_csrf_protection_enabled_for_html_forms(self):
        """Test that CSRF protection is enabled for HTML forms (Admin Login)"""
        response = self.client.get(self.admin_login_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("csrfmiddlewaretoken", response.content.decode())

    def test_csrf_protection_not_required_for_api(self):
        """Test that API endpoints do not require CSRF token"""
        response = self.client.post(self.register_url, {
            "username": "apiuser",
            "email": "apiuser@example.com",
            "password": "SecureP@ssw0rd123"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
