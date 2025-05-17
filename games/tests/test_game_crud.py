from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from games.models import Game
from users.models import CustomUser

class GameCRUDTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        cls.game_list_url = reverse('game-list')
        cls.game = Game.objects.create(
            title="Beer Pong",
            description="Classic party game",
            creator=cls.user
        )
        cls.game_detail_url = reverse('game-detail', kwargs={'pk': cls.game.pk})

    def test_create_game(self):
        self.client.login(username="testuser", password="password123")
        data = {
            "title": "Kings Cup",
            "description": "Fun drinking game",
            "rules": "Shuffle the deck and draw cards"
        }
        response = self.client.post(self.game_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Game.objects.count(), 2)

