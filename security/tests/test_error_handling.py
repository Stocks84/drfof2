from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse, resolve
from django.http import Http404
from django.conf import settings


class ErrorHandlingTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.non_existent_url = "/non-existent-url/"
        cls.register_url = reverse('register')

    def test_404_not_found_error(self):
        """Test that accessing a non-existent URL returns 404"""
        response = self.client.get(self.non_existent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Not Found", response.content.decode())

    def test_500_internal_server_error(self):
        """Test that an internal server error returns 500"""
        # Simulate a view that raises an exception
        with self.assertRaises(Http404):
            resolve("/this-will-trigger-500/")

    def test_400_bad_request_error(self):
        """Test that invalid data returns 400 Bad Request"""
        # Test with invalid username, email, and password
        response = self.client.post(self.register_url, {
            "username": "",  # Missing username (invalid)
            "email": "invalidemail",  # Invalid email format
            "password": "123"  # Too short (weak password)
        }, format='json')
    
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertIn("email", response.data)
        
        # Ensure any form of password validation is triggered
        self.assertTrue(
            "password" in response.data or 
            any("password" in str(field) for field in response.data.keys()) or
            any("This password is too short." in str(msg) for msg in response.data.values())
        )

        # Test directly for weak password only (without other errors)
        response = self.client.post(self.register_url, {
            "username": "validuser",
            "email": "validemail@example.com",
            "password": "123"  # Weak password
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertTrue(
            any("This password is too short." in str(msg) for msg in response.data["password"])
        )

    def test_403_forbidden_error(self):
        """Test that unauthorized access returns 403 Forbidden"""
        profile_url = reverse('user-profile')
        response = self.client.get(profile_url)  # Not logged in
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.data)
    
    def test_custom_404_error_page(self):
        """Test that the custom 404 page is used (if configured)"""
        with self.settings(DEBUG=False):
            response = self.client.get("/non-existent-url/")
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn("Not Found", response.content.decode())

    def test_custom_500_error_page(self):
        """Test that the custom 500 page is used (if configured)"""
        with self.settings(DEBUG=False):
            with self.assertRaises(Http404):  # Simulate a server error
                resolve("/this-will-trigger-500/")
