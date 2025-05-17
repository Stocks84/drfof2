from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from users.models import CustomUser


class SensitiveDataTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        cls.profile_url = reverse('user-profile')

    def test_sensitive_data_not_exposed(self):
        """Test that user password is not exposed in API responses"""
        self.client.login(username="testuser", password="password123")
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("password", response.data)
