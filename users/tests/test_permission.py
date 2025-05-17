from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from users.models import CustomUser


class PermissionTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        cls.profile_url = reverse('user-profile')

    def test_unauthorized_access_restricted(self):
        """Test that unauthorized users cannot access protected endpoints"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authorized_access_granted(self):
        """Test that authorized users can access protected endpoints"""
        self.client.login(username="testuser", password="password123")
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
