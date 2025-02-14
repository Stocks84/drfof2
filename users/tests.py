from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import CustomUser

class UserProfileTest(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        # Correct URLs with 'api' prefix
        self.login_url = reverse('token_obtain_pair')        # /api/token/
        self.profile_url = reverse('user-profile')           # /api/profile/

    def test_retrieve_user_profile(self):
        # Obtain JWT token
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'password123'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data['access']

        # Retrieve profile using token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
