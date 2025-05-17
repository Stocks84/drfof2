from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from users.models import CustomUser


class UserManagementTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        cls.register_url = reverse('register')
        cls.profile_url = reverse('user-profile')
        cls.password_change_url = reverse('change-password')
        cls.delete_account_url = reverse('delete-account')

    def setUp(self):
        # Login for authenticated tests
        self.client.login(username="testuser", password="password123")

    # --- User Registration Tests ---
    def test_user_registration(self):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CustomUser.objects.filter(username="newuser").exists())

    def test_registration_with_existing_username(self):
        data = {
            "username": "testuser",  # Username already exists
            "email": "anotheruser@example.com",
            "password": "anotherpassword123"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- User Profile Tests ---
    def test_retrieve_user_profile(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_update_user_profile(self):
        data = {"bio": "Updated bio", "favorite_drink": "Whiskey Sour"}
        response = self.client.patch(self.profile_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.bio, "Updated bio")

    def test_unauthenticated_profile_access(self):
        self.client.logout()
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Password Change Tests ---
    def test_password_change(self):
        data = {
            "old_password": "password123",
            "new_password": "NewSecurePass456!"
        }
        response = self.client.post(self.password_change_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the new password works
        self.client.logout()
        login_response = self.client.post(reverse('token_obtain_pair'), {
            "username": "testuser",
            "password": "NewSecurePass456!"
        }, format="json")
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

    def test_password_change_with_incorrect_old_password(self):
        data = {
            "old_password": "wrongpassword",
            "new_password": "NewSecurePass456!"
        }
        response = self.client.post(self.password_change_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Account Deletion Tests ---
    def test_user_deletion(self):
        response = self.client.delete(self.delete_account_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CustomUser.objects.filter(username="testuser").exists())

    def test_unauthenticated_user_deletion(self):
        self.client.logout()
        response = self.client.delete(self.delete_account_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
