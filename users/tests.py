from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import CustomUser


class UserProfileTest(APITestCase):
    def setUp(self):
        """Set up a test user and obtain JWT token"""
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.login_url = reverse('token_obtain_pair')        # /api/token/
        self.profile_url = reverse('user-profile')           # /api/profile/
        self.password_change_url = reverse('change-password')  # /api/change-password/
        self.delete_account_url = reverse('delete-account')   # /api/delete-account/

        # Obtain JWT token
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'password123'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.access_token = response.data['access']

        # Authenticate all requests
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_retrieve_user_profile(self):
        """Test that an authenticated user can retrieve their profile"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_update_user_profile(self):
        """Test that an authenticated user can update their profile"""
        data = {"bio": "Updated bio", "favorite_drink": "Whiskey Sour"}
        response = self.client.patch(self.profile_url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.bio, "Updated bio")
        self.assertEqual(self.user.favorite_drink, "Whiskey Sour")

    def test_password_change(self):
        """Test that an authenticated user can change their password"""
        data = {
            "old_password": "password123",
            "new_password": "NewSecurePass456!"
        }
        response = self.client.post(self.password_change_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify that the old password no longer works
        self.client.credentials()  # Reset authentication
        login_response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "password123"
        }, format="json")
        self.assertEqual(login_response.status_code, status.HTTP_401_UNAUTHORIZED)  # Old password should fail

        # Verify that the new password works
        new_login_response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "NewSecurePass456!"
        }, format="json")
        self.assertEqual(new_login_response.status_code, status.HTTP_200_OK)

    def test_user_deletion(self):
        """Test that an authenticated user can delete their account"""
        response = self.client.delete(self.delete_account_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CustomUser.objects.filter(username="testuser").exists())
