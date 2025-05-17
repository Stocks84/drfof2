from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from games.models import Game
from users.models import CustomUser


class SQLInjectionTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        cls.game_list_url = reverse('game-list')

    def test_sql_injection_attempt(self):
        """Test that SQL injection does not work"""
        response = self.client.get(f"{self.game_list_url}?title=' OR 1=1 --")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("Internal Server Error", response.content.decode())
