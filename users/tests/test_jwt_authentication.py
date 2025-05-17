from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from users.models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken


class JWTAuthenticationTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        cls.token_obtain_url = reverse('token_obtain_pair')  # /api/token/
        cls.token_refresh_url = reverse('token_refresh')     # /api/token/refresh/

    def test_jwt_token_obtain(self):
        """Test obtaining JWT access and refresh tokens"""
        response = self.client.post(self.token_obtain_url, {
            "username": "testuser",
            "password": "password123"
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_jwt_token_obtain_invalid_credentials(self):
        """Test JWT token obtain with invalid credentials"""
        response = self.client.post(self.token_obtain_url, {
            "username": "testuser",
            "password": "wrongpassword"
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_token_refresh(self):
        """Test refreshing JWT token"""
        # Obtain JWT tokens
        response = self.client.post(self.token_obtain_url, {
            "username": "testuser",
            "password": "password123"
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        refresh_token = response.data["refresh"]

        # Use the refresh token to get a new access token
        response = self.client.post(self.token_refresh_url, {
            "refresh": refresh_token
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_jwt_token_refresh_with_invalid_token(self):
        """Test refreshing JWT with an invalid token"""
        response = self.client.post(self.token_refresh_url, {
            "refresh": "invalid_refresh_token"
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_access_token_for_authenticated_requests(self):
        """Test using JWT access token for authenticated requests"""
        # Obtain JWT tokens
        response = self.client.post(self.token_obtain_url, {
            "username": "testuser",
            "password": "password123"
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data["access"]

        # Use access token for an authenticated request
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_url = reverse('user-profile')
        response = self.client.get(profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_jwt_refresh_token_cannot_access_protected_route(self):
        """Test that refresh token cannot be used for protected routes"""
        # Obtain JWT tokens
        response = self.client.post(self.token_obtain_url, {
            "username": "testuser",
            "password": "password123"
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        refresh_token = response.data["refresh"]

        # Attempt to use refresh token for an authenticated request
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh_token}')
        profile_url = reverse('user-profile')
        response = self.client.get(profile_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
